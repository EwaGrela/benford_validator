# Description
1. A Flask app is created in app.py
2. Static data - generated charts are stored in 'static' folder in docker container 
3. Instruction creating database is stored in create_db.py file
4. app.py contains a very small REST API containing endpoint used to validate file
   It contains a Flask form which is used to upload file 

5. A class called DataframeValidator validates the files uploaded by user and transforms it into DataFrame
    using pandas library
   - file is validated - only certain types are accepted - byte files and .csv and .tsv files
   - user is told they should keep the data they want to validate in a third column
   - if file is validated, the name of the column in which data is kept changes its name to 'my_data'
   
6. A class called BenfordValidator performs the most important task - validating if data in column follows the 
    principles of Benford's Law
    - once the file is validated, data from third column is retrieved
    - BenfordValidator performs tests and final results - a chart with info - are stored in static folder
      and a chart is rendered and presented to user

7. BenfordValidator's methods are as follows:
    - count_first_digit()
        returns data_count ( 9 element list with how many numbers of dataset begin with each digit)
        total_count = lenght of dataset
        data_percentage = what is the % of each first digit in a dataset
    - get_expected_counts()
        calculates what the distribution of data should be according to Benford's Law
    - chi_square_test()
        based on data_count and expected_counts a chi square test is performed
    - build_chart()
        a chart is drawn and saved into static folder/presented to user

8. Tests are stored in tests.py file, DataframeReader and BenfordValidator are tested


9. App is dockerized. In the main folder of an app:
```
cd zadanie3
sudo docker-compose build
sudo docker-compose up
```

10. Tests can be run from inside the docker container
    Run the app ( see 9.)
    Then:
```
sudo docker ps
sudo docker exec -it container_id  bash
python tests.py
```

11. The app contains several endpoints:

### `/`
* **GET, POST**
 A form which ingests file. A file is then validated, if it is invalid, user gets info
 Valid file must be .tsv, .csv or flat file, its third column must be numeric and it is renamed to 'my_data'.
 We assume (inform the user) they must put data they want analysed into third column
 In this endpoint, our data is transformed into dataframe and put into database.
 Class db_manager.DatabaseManager deals with all operations on database.
 Valid data is analysed, an instance od BenfordValidator class performs validity test
 A chart is output and put into 'static' folder

### `/names`
* **GET**
    A complete list of all dataset names
    By clicking on the name on the list, user can create a chart with expected/input data to see if this dataset follows Benford's Law
    By clicking the download button one can download the given dataset

### `/dataset/<name>`
* **GET**
    Dataset from database can be downloaded and then further analysed if it follows Benford's Law or
    for other purposes

### `/analyze_dataset/<name>`
* **GET**
    Dataset from database is validated and user sees if dataset follows Benford's Law

12. Class DatabaseManager deals with database persistence
    Its methods are:
    - gather_df() - puts the df as table into database
    - retrieve_df() - retrieves data from database 
    - retrieve_df_names() - retrieves list of available datasets' names
    - gather_df_names() - when df is put into database, it's name is added to df_names table
