"""
Example of a web scrapper for job offers posted on LinkedIn.

This was made using the guide posted by Viola Mao on medium.com
Original link: https://maoviola.medium.com/a-complete-guide-to-web-scraping-linkedin-job-postings-ad290fcaa97f

"""

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from tqdm import tqdm
import urllib.parse
import pandas as pd
import time



def main():
    """
    Runs all the tasks needed for the scrapping process.
    :return:
    """
    get_data("Ingeniero de datos", headless_mode=False)


def get_data(search_terms, headless_mode=True):
    """
    Uses Selenium WebDriver for Chrome to do a search on the jobs for the keywords in the search_terms parameter,
    that are available in Chile. It fetches all the data into a Pandas dataframe and then writes a Excel file for
    further analysis.

    :return:
    """

    search_terms = urllib.parse.quote_plus(search_terms)

    # URL to visit in anonymous mode
    url = f"https://www.linkedin.com/jobs/search?keywords={search_terms}&location=Chile" \
          + "&geoId=104621616&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0"

    # Create a Chrome driver in headless mode
    service = Service("D://Tools//chromedriver.exe")
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")

    if headless_mode:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")

    print("Starting a web session for the URL:", url)
    wd = webdriver.Chrome(service=service, options=options)
    wd.get(url)

    # Read from the label shown in screen, the total amount of jobs found by the LinkedIn search service
    total_count = int(
        wd.find_element(By.CSS_SELECTOR, "h1 > .results-context-header__job-count").get_attribute("innerText"))
    print("Total jobs found:", total_count)

    """Scroll through the list of job offers, to load more items. If we reach the bottom of the list, try to
    click on the "Show more" button"""
    count_pages = int(total_count / 25) + 1
    print(f"Considering 25 items per page, we will load {count_pages} pages.")

    for _ in tqdm(range(count_pages)):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            wd.find_element(By.CSS_SELECTOR, "button.infinite-scroller__show-more-button").click()
            time.sleep(5)
        except:
            pass
            time.sleep(5)

    jobs_list = wd.find_element(By.CSS_SELECTOR, ".jobs-search__results-list")
    jobs = jobs_list.find_elements(By.TAG_NAME, "li")

    print("Amount of jobs listed:", len(jobs))

    # Load basic data from the list of jobs
    job_id = []
    job_title = []
    company_name = []
    location = []
    date = []
    job_link = []
    jd = []
    seniority = []
    emp_type = []
    industries = []

    for job in tqdm(jobs):
        job_id0 = job.find_element(By.TAG_NAME, "div").get_attribute("data-entity-urn")
        job_id.append(job_id0)

        job_title0 = job.find_element(By.CSS_SELECTOR, "h3.base-search-card__title").get_attribute("innerText")
        job_title.append(job_title0)

        company_name0 = job.find_element(By.CSS_SELECTOR, "h4.base-search-card__subtitle").get_attribute("innerText")
        company_name.append(company_name0)

        location0 = job.find_element(By.CSS_SELECTOR, '[class="job-search-card__location"]').get_attribute("innerText")
        location.append(location0)

        date0 = job.find_element(By.CSS_SELECTOR, "time").get_attribute("datetime")
        date.append(date0)

        link = job.find_element(By.CSS_SELECTOR, "a")
        job_link0 = link.get_attribute("href")
        job_link.append(job_link0)

        # Click on the job's link to get more details
        try:
            link.click()
            time.sleep(3)     # Wait for the interface to load job's data
        except Exception as e:
            print("Got an error while clicking on item: ", e)
            pass

        try:
            jd_path = "/html/body/div[1]/div/section/div[2]/div/section[1]/div/div/section/div"
            jd0 = wd.find_element(By.XPATH, jd_path).get_attribute("innerText")
        except:
            jd0 = ""

        jd.append(jd0)

        try:
            seniority_path = "/html/body/div[1]/div/section/div[2]/div/section[1]/div/ul/li[1]/span"
            seniority0 = wd.find_element(By.XPATH, seniority_path).get_attribute("innerText")
        except:
            seniority0 = ""

        seniority.append(seniority0)

        try:
            emp_type_path = "/html/body/div[1]/div/section/div[2]/div/section[1]/div/ul/li[2]/span"
            emp_type0 = wd.find_element(By.XPATH, emp_type_path).get_attribute("innerText")
        except:
            emp_type0 = ""

        emp_type.append(emp_type0)

        try:
            industries_path = "/html/body/div[1]/div/section/div[2]/div/section[1]/div/ul/li[4]/span"
            industries0 = wd.find_element(By.XPATH, industries_path).get_attribute("innerText")
        except:
            industries0 = ""

        industries.append(industries0)

    # Close the web browser instance
    wd.quit()

    job_data = pd.DataFrame({"ID": job_id,
                             "Date": date,
                             "Company": company_name,
                             "Title": job_title,
                             "Location": location,
                             "Description": jd,
                             "Level": seniority,
                             "Type": emp_type,
                             "Industry": industries,
                             "Link": job_link
                             })

    # Clean new lines in Description attribute
    job_data["Description"] = job_data["Description"].str.replace("\n", " ")

    # Save as JSON file with timestamp in the file name
    path = "data/linkedin_jobs_data_{}.json".format(datetime.timestamp(datetime.now()))
    print("Data will be saved as:", path)
    job_data.to_json(path)

    print("Finished!")


if __name__ == "__main__":
    main()
