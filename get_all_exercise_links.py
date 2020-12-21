from selenium import webdriver
from selenium.webdriver.firefox.webdriver import FirefoxProfile
from selenium.webdriver.chrome.options import Options
import time
from collections import namedtuple
from collections import defaultdict
from argparse import ArgumentParser

TableLine = namedtuple('TableLine', ['candidate', 'comission', 'total_score', 'grade', 'row'])


def read_data_from_table(table):
    table_lines = []
    table_rows = table.find_elements_by_tag_name('tr')

    for row in table_rows[1:]:  # Skip header
        columns = row.find_elements_by_tag_name('td')
        table_lines.append(TableLine(candidate=columns[0].text, comission=columns[1].text,
                                     total_score=columns[2].text, grade=columns[3].text, row=row))

    return table_lines


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-u', '--username', type=str, required=True)
    parser.add_argument('-p', '--password', type=str, required=True)
    parser.add_argument('-o', '--outputfile')

    args = parser.parse_args()
    username = args.username
    password = args.password
    outputfile = args.outputfile

    # driver = webdriver.Firefox(profile)
    driver = webdriver.Chrome(executable_path=r"C:\utilities\chromedriver.exe")
    driver.get('https://uio.inspera.no/admin#grading/details/72455329?committeeId=194602')

    time.sleep(5)
    login_link = driver.find_element_by_id('loginWithLocalUserTrigger')
    login_link.click()
    username_field = driver.find_element_by_xpath(
        '/html/body/div[5]/div[1]/div/div[2]/div[1]/div[3]/div[11]/form/fieldset/div[1]/input')
    password_field = driver.find_element_by_xpath(
        '/html/body/div[5]/div[1]/div/div[2]/div[1]/div[3]/div[11]/form/fieldset/div[2]/input')
    login_button = driver.find_element_by_xpath(
        '/html/body/div[5]/div[1]/div/div[2]/div[1]/div[3]/div[11]/form/fieldset/button/span')
    username_field.send_keys(username)
    password_field.send_keys(password)
    login_button.click()
    time.sleep(4)

    question_to_links = defaultdict(list)

    try:
        current_line = 0
        candidates_table = driver.find_element_by_xpath(
            r'/html/body/div[5]/div[1]/div/div[2]/div/div/div[3]/div[2]/div/table')
        candidate_table_lines = read_data_from_table(candidates_table)
        while current_line < len(candidate_table_lines):
            # Go to a specific candidate
            candidate_table_lines[current_line].row.click()
            time.sleep(2)

            question_index = 0
            question_links = driver.find_elements_by_class_name('question-title')
            while question_index < len(question_links):
                question_text = question_links[question_index].text
                question_links[question_index].click()
                time.sleep(2)
                question_to_links[question_text].append(driver.current_url)

                # Go back to questions
                candidate_link = driver.find_element_by_xpath('/html/body/div[5]/div[1]/div/div[1]/div[1]/div[1]/a/span')
                candidate_link.click()
                time.sleep(2.2)

                question_links = driver.find_elements_by_class_name('question-title')
                question_index += 1

            # Go back
            candidates_link = driver.find_element_by_xpath('/html/body/div[5]/div[1]/div/div[1]/div[1]/div[1]/a/span')
            candidates_link.click()
            time.sleep(2)

            # Refresh table, as they have become stale due to changing page
            candidates_table = driver.find_element_by_xpath(
                r'/html/body/div[5]/div[1]/div/div[2]/div/div/div[3]/div[2]/div/table')
            candidate_table_lines = read_data_from_table(candidates_table)
            current_line += 1

    except Exception:
        with open(outputfile, 'w') as fp:
            for question, links in question_to_links.items():
                for link in links:
                    fp.write("{};{}\n".format(question, link))

    with open(outputfile, 'w') as fp:
        for question, links in question_to_links.items():
            for link in links:
                fp.write("{};{}\n".format(question, link))

