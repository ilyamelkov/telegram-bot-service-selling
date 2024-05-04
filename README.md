# **Telegram Bot project**

## **Motivation**
- Practice **MySQL** and **Python** simultaneously;
- Practice **data manipulation** using Pandas;
- Try to create a **database from scratch**

## **Project's main steps** 
1. Design and create a database containing all relevant information 
2. Create a Telegram Bot which will be able to successfully pass data from a database to a user and vice versa

## **Description of files in a directory**
1. Database-related files:

    * <ins>sql_fun.py</ins>
        * Functions for easier SQL database creation
    * <ins>generate_db.ipynb</ins>
        * File which creates database and adds data to it  
    * <ins>alter_check_db.py</ins>
        * Functions that alter database information
    * <ins>queries_fun.py</ins>
        * Functions that retrieve data from the specific database used in this project

2. Bot-related files:
    * <ins>bot_fun.py</ins>
        * Functions for a bot 
    * <ins>bot_aiogram.py</ins> 
        * Code for the bot itself

3. Other files:
    * <ins>constants.py</ins>
        * Contains constant values which can be altered
    * <ins>data_st.py</ins>
        * Contains dictionaries where user's choices are saved
    * <ins>ERD.jpg</ins>
        * Visual representation of the database structure

## **Database design**
* This is how resulting database looks like (the image was created using DB Visualizer Software): 
 
  ![DB structure](/ERD.jpg)

## **Bot features**
- Create appointments based on available date/available employee.
- View your upcoming appointments and cancel them if you would like to.
- View prices for services.

## **Demonstration**
https://github.com/ilyamelkov/telegram-bot-service-selling/assets/109285166/513168d4-3702-43f1-88b7-83d4cb9ff68c


## **Possible usage**
- The data itself can be modified by other people. The bot can be reused considering the same database structure.
