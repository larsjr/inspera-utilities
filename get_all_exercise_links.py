from selenium import webdriver
from selenium.webdriver.firefox.webdriver import FirefoxProfile
from selenium.webdriver.chrome.options import Options
import pathlib, platform, progressbar, time
from collections import namedtuple
from collections import defaultdict
from argparse import ArgumentParser
import sys

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

    system = platform.system()
    if system == "Windows":
        chromedriver = r"C:\utilities\chromedriver.exe"
    elif system == "Linux":
        chromedriver = "chromedriver"
    else:
        sys.stderr.write("OS not supported.")
        sys.exit(1)

    parser = ArgumentParser()
    parser.add_argument('-o', '--outputfile',  type=str, required=True,  help="Outputfile to be read by open_and_log_excercises.py")
    parser.add_argument('-c', '--commission',  type=str, required=True,  help="Link to commission")
    parser.add_argument('-u', '--username',    type=str, required=False, help="Username (skip to use manual login)")
    parser.add_argument('-p', '--password',    type=str, required=False, help="Password (skip to use manual login)")

    args = parser.parse_args()
    username = args.username
    password = args.password
    outputfile = args.outputfile
    commission = args.commission

    # driver = webdriver.Firefox(profile)
    driver = webdriver.Chrome(executable_path=chromedriver)
    driver.get(commission)

    if username and password:
        time.sleep(10)
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
    else:
        print("Manual login. You have 40 seconds..")
        time.sleep(40)

    question_to_links = defaultdict(list)

    assignments = 14

    try:
        current_line = 0
        candidates_table = driver.find_element_by_xpath(
            r'/html/body/div[5]/div[1]/div/div[2]/div/div/div[3]/div[2]/div/table')
        candidate_table_lines = read_data_from_table(candidates_table)
        total_assignments = len(candidate_table_lines)*assignments
        bar = progressbar.ProgressBar(maxval=total_assignments)
        bar.start()
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

                bar.update(current_line*assignments + question_index)

            # Go back
            candidates_link = driver.find_element_by_xpath('/html/body/div[5]/div[1]/div/div[1]/div[1]/div[1]/a/span')
            candidates_link.click()
            time.sleep(2)

            # Refresh table, as they have become stale due to changing page
            candidates_table = driver.find_element_by_xpath(
                r'/html/body/div[5]/div[1]/div/div[2]/div/div/div[3]/div[2]/div/table')
            candidate_table_lines = read_data_from_table(candidates_table)
            current_line += 1
        bar.finish()

    except Exception as e:
        print("An Exception occurred. Perhaps Inspera is not responsive right now? Details: {}".format(str(e)))
        with open(outputfile, 'w') as fp:
            for question, links in question_to_links.items():
                for link in links:
                    fp.write("{};{}\n".format(question, link))

    with open(outputfile, 'w') as fp:
        for question, links in question_to_links.items():
            for link in links:
                fp.write("{};{}\n".format(question, link))

