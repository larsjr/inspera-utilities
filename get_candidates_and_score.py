from selenium import webdriver
import time
import argparse
from collections import namedtuple

TableLine = namedtuple('TableLine', ['candidate', 'comission', 'total_score', 'grade'])


def read_data_from_table(table):
    table_lines = []
    table_rows = table.find_elements_by_tag_name('tr')

    for row in table_rows[1:]:  # Skip header
        columns = row.find_elements_by_tag_name('td')
        table_lines.append(TableLine(candidate=columns[0].text, comission=columns[1].text,
                                     total_score=columns[2].text, grade=columns[3].text))

    return table_lines


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', type=str, required=True)
    parser.add_argument('-p', '--password', type=str, required=True)
    parser.add_argument('-o', '--output', type=str, required=True)
    parser.add_argument('-a', '--address', type=str, required=True)

    args = parser.parse_args()

    driver = webdriver.Firefox()
    driver.get(args.address)
    time.sleep(5)
    login_link = driver.find_element_by_id('loginWithLocalUserTrigger')
    login_link.click()
    username = driver.find_element_by_xpath('/html/body/div[5]/div[1]/div/div[2]/div[1]/div[3]/form/fieldset/div[1]/input')
    password = driver.find_element_by_xpath('/html/body/div[5]/div[1]/div/div[2]/div[1]/div[3]/form/fieldset/div[2]/input')
    login_button = driver.find_element_by_xpath('//*[@id="main"]/div/div[2]/div[1]/div[3]/form/fieldset/button')
    username.send_keys(args.user)
    password.send_keys(args.password)
    login_button.click()

    time.sleep(3)

    #commision_7 = driver.find_element_by_xpath('//*[@id="grading-overview-panel"]/div[3]/div[2]/div[2]/div[1]/span[2]/a')
    #commision_7.click()
    #time.sleep(2)

    table = driver.find_element_by_xpath('/html/body/div[5]/div[1]/div/div[2]/div/div/div[3]/div[2]/div/table')

    lines = read_data_from_table(table)

    second_page_link = driver.find_element_by_id('pagination_pages_page_2')
    second_page_link.click()
    time.sleep(2)

    table2 = driver.find_element_by_xpath('/html/body/div[5]/div[1]/div/div[2]/div/div/div[3]/div[2]/div/table')
    lines2 = read_data_from_table(table2)
    lines.extend(lines2)

    print('Found {} candidates'.format(len(lines)))
    with open(args.output, 'w') as fp:
        for line in lines:
            fp.write('{},{},{},{}\n'.format(line.candidate, line.comission, line.total_score, line.grade))


