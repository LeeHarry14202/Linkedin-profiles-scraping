from selenium import webdriver
from selenium.webdriver.common.keys import Keys
# The sleep function helps slow down the execution from out script for given number of seconds
from time import sleep
# Pull data out of HTML files, which is the file that stores the content of website
from bs4 import BeautifulSoup
import csv

# Task 1: Login to Linkedin
# Load Chrome driver
your_chromedriver_path = ''
driver = webdriver.Chrome(your_chromedriver_path)


def go_to_linkedin():
    # Link of web
    url = 'https://www.linkedin.com/login'
    # Open web
    driver.get(url)


credential = open('login_credential.txt')
# Read each line in login_credential.txt
line = credential.readlines()
username = line[0]
password = line[1]


# Autofill email
def autofill_email():
    email_field = driver.find_element_by_xpath('//*[@id="username"]')
    email_field.send_keys(username)
    sleep(2)


# Autofill password
def autofill_password():
    password_field_name = 'session_password'
    password_field = driver.find_element_by_name(password_field_name)
    password_field.send_keys(password)
    sleep(3)


# Auto click sign in
def autoclick_sign_in():
    login_field_xpath = '//*[@id="organic-div"]/form/div[3]/button'
    login_field = driver.find_element_by_xpath(login_field_xpath)
    login_field.click()
    sleep(2)


def auto_login():
    autofill_email()
    autofill_password()
    autoclick_sign_in()


#  Task2: Search for the profile we want to crawl
def see_all_people_results():
    class_ = "artdeco-pill"
    see_all_people_results = driver.find_element_by_class_name(class_)
    see_all_people_results.click()
    sleep(2)


def search():
    # The xpath of the search bar
    search_field_xpath = '//*[@id="global-nav-typeahead"]/input'
    # Locate the search bar element
    search_field = driver.find_element_by_xpath(search_field_xpath)
    # Input search query to the search bar
    search_query = 'software engineer people'  # input('What profile do you want to search: ')
    # Input text to search bar
    search_field.send_keys(search_query)
    sleep(2)

    # Search
    search_field.send_keys(Keys.ENTER)
    sleep(3)

    see_all_people_results()


# Task 3: Open the URLs of the profiles

def getURL():
    # Load page_source
    page_source = BeautifulSoup(driver.page_source)
    # Locate URL profile
    profiles = page_source.find_all('a', class_='app-aware-link')
    # Create a list will contains URL profile on one page
    list_profile_URL = []
    max_profile_one_page = 10
    profile_count_one_page = 0
    remove_Linkedin_Member = 'https://www.linkedin.com/search/results/people/headless?origin=SWITCH_SEARCH_VERTICAL&keywords=software%20engineer%20people'
    # Use loop to get many URL profile on one page
    for profile in profiles:
        # href address contains URL profile
        profile_URL = profile.get('href')
        if profile_URL not in list_profile_URL and profile_URL != remove_Linkedin_Member:
            # Add URL profile to list
            list_profile_URL.append(profile_URL)
            profile_count_one_page += 1
        if profile_count_one_page == max_profile_one_page:
            # if True stop the loop
            break
    # Remove ad href address, usually is the first element in list
    list_profile_URL.pop(0)
    return list_profile_URL


def getURLsonPages(number_of_page):
    # Create a list will contains many URL profiles
    URLs_all_page = []
    for page in range(number_of_page):
        URLs_one_page = getURL()
        sleep(3)

        # Scroll to next button, if don't have this, it will not define where is the next button
        scroll_to_next_button = 'window.scrollTo(0,document.body.scrollHeight);'
        driver.execute_script(scroll_to_next_button)
        sleep(3)

        # Click the next button
        next_button_class = 'artdeco-pagination__button--next'
        next_button = driver.find_element_by_class_name(next_button_class)
        next_button.click()
        sleep(3)

        # Add list one page to all page
        URLs_all_page = URLs_all_page + URLs_one_page
        sleep(3)
    return URLs_all_page


# Task 4: Scrape each profile & Write the data to a .CSV file
## Task 4.1: Write a function to access and scrape the data of 1 Linkedin profile
def get_personal_info(personal_linkedin_URL):
    # for personal_linkedin_URL in URLs_all_page:
    # Go to each URL page
    driver.get(personal_linkedin_URL)
    sleep(2)
    # Get current URL page source
    page_source = BeautifulSoup(driver.page_source, 'html.parser')
    # Get info tag
    info_div = page_source.find('div', class_='pv-text-details__left-panel mr5')
    # Get name tag from info tag by get_text() function and remove blank space with strip()
    name = info_div.find('h1').get_text().strip()
    # Same name tag
    current_position = info_div.find(class_='text-body-medium break-words').get_text().strip()
    # Same name tag
    country = info_div.find(class_='text-body-small inline t-black--light break-words').get_text().strip()

    # Create a list contains 3 values: name, current_position, country
    list_personal_info = []
    list_personal_info.append(name)
    list_personal_info.append(current_position)
    list_personal_info.append(country)

    # Return list personal info of one person
    return list_personal_info


## Task 4.2: Write the output to a .CSV file


def export_output_to_csv():
    number_of_page = 100  # int(input('How many pages you want to scrape: '))
    URLs_all_page = getURLsonPages(number_of_page)

    # Open and close  file output.csv
    with open('output.csv', 'w', newline='') as file_output:
        # Create 4 headers tittle
        headers = ['Name', 'Current Position', 'Country', 'URL']
        # Write profile to file csv by DictWriter
        writer = csv.DictWriter(file_output, delimiter=',', lineterminator='\n', fieldnames=headers)
        # Write headers to file csv
        writer.writeheader()

        # Get info profile and write it to csv file in URL_all_page
        for personal_linkedin_URL in URLs_all_page:
            # personal_info is a list have 3 values: name, current_position, country
            personal_info = get_personal_info(personal_linkedin_URL)

            # Situation index in personal_info list
            name_index = 0
            current_position_index = 1
            country_index = 2
            name = personal_info[name_index]
            current_position = personal_info[current_position_index]
            country = personal_info[country_index]

            writer.writerow({headers[0]: name, headers[1]: current_position, headers[2]: country,
                             headers[3]: personal_linkedin_URL})


if __name__ == '__main__':
    go_to_linkedin()
    auto_login()
    search()
    export_output_to_csv()
