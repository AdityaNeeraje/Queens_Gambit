from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException
from time import sleep
import json

url='https://www.math.ucla.edu/~tom/Games/chomp.html'

options=webdriver.ChromeOptions()
# options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
driver.get(url)

with open('4x7_winning_moves.json') as f:
    winning_moves=json.load(f)

max_number_of_attempts=20
sleep_time=5

while True:
    game_pos='.'*28
    for i in range(max_number_of_attempts):
        try:
            active_links=driver.find_elements(By.CSS_SELECTOR, 'form[name="game"] table a')
        except Exception as e:
            if i==max_number_of_attempts-1:
                print('Error:', e)
                exit()
            else:
                sleep(sleep_time)         
    for link in active_links:
        if link.find_element(By.CSS_SELECTOR, 'img').get_attribute('src').endswith('blank.gif'):
            id=link.get_attribute('href').split(',')
            index_to_replace=(int(id[0][-1])-1)*7+int(id[1][0])-1
            game_pos=game_pos[:index_to_replace]+'X'+game_pos[index_to_replace+1:]
    winning_move=winning_moves[game_pos]
    min_x=7
    min_y=4
    for i in range(28):
        if game_pos[i]!=winning_move[i]:
            min_x=min(i%7, min_x)
            min_y=min(i//7, min_y)
    for i in range(max_number_of_attempts):
        try:
            driver.find_element(By.CSS_SELECTOR, 'form[name="game"] table a[href="javascript:yourChoice('+str(min_y+1)+','+str(min_x+1)+')"]').click()
        except (ElementClickInterceptedException, ElementNotInteractableException):
            element=driver.find_element(By.CSS_SELECTOR, 'form[name="game"] table a[href="javascript:yourChoice('+str(min_y+1)+','+str(min_x+1)+')"]')
            driver.execute_script("arguments[0].click();", element)
        except Exception as e:
            if i==max_number_of_attempts-1:
                print('Error:', e)
                exit()
            else:
                sleep(sleep_time)
    sleep(1)
    if winning_move=='.'+'X'*27:
        print("Hey, we won")
        break

driver.quit()