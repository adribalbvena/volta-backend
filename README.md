## SET UP VOLTA API:
1. Clone this project
2. In workbench open the **Volta_db_queries.sql** file and run the first statement `CREATE DATABASE volta;` to create the db.
3. Ensure that the virtual environment for the project is set up. If you haven't set up a virtual environment, it's recommended to create one before proceeding. You can do this by going to File -> Settings -> Project -> Python Interpreter and clicking on the gear icon to create a new virtual environment.
4. Open the project in PyCharm and install the packages listed in the **requirements.txt** file either by:
   1. running the following command: `pip install -r requirements.txt`
   2. or you can install the packages one by one, by putting your mouse over the import and clicking 'install package...'
5. In the root directory create the **.env** file and set:
    1. **SECRET_KEY=yoursecretkey**
    2. **PLAN_KEY=provided with the source code link**
6. In **config.py**  line 11 set your local mysql database user name and password
7. Download a local instance of Redis to store the session data:
   1. if you have Windows: https://github.com/MicrosoftArchive/redis/releases the 3.2.100 version (.msi file).
   2. if you have Mac you can use the brew command: `brew install redis`
8. Run the main file.
9. You can test the API using the provided postman collection, or you can run the frontend part.

Let’s clone and set up the frontend now!:  https://github.com/adribalbvena/volta-frontend