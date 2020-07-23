import pymysql
import warnings
warnings.filterwarnings("error",category=pymysql.Warning)


class DB:

    def __init__(self):
        
        self.connections = pymysql.connect(
            host="localhost",
            user="yaroslav",
            password="yariksun4002",
            db="currencybotv2"
            )

        self.cursor = self.connections.cursor() 


        def _create_or_pass_table(query_to_check):
            for execution in query_to_check:
                try:
                    self.cursor.execute(execution)
                except Warning:
                    pass

        
        create_user_table = "CREATE TABLE IF NOT EXISTS users (id INT NOT NULL ,name VARCHAR(30) NOT NULL)"
        create_track_currancy_table = "CREATE TABLE IF NOT EXISTS track_currency (id INT NOT NULL,currency CHAR(3) NOT NULL,curr_from CHAR(30) NOT NULL,curr_to CHAR(30) NOT NULL)"
        create_currant_currency_table = "CREATE TABLE IF NOT EXISTS current_currency (currency CHAR(3) NOT NULL,rate FLOAT NOT NULL,date DATE NOT NULL)"
        _create_or_pass_table([create_user_table,create_track_currancy_table,create_currant_currency_table])
          
            
    

    def write_user(self,user_id,user_name):
        write_user = "INSERT INTO users VALUES('{}','{}')".format(user_id,user_name)
        self.cursor.execute(write_user)
        self.connections.commit()
        

    def write_track_currancy(self,user_id,currency,curr_from,curr_to):
        track_currancy = "INSERT INTO track_currency VALUES('{}','{}','{}','{}')".format(user_id,currency,curr_from,curr_to)
        self.cursor.execute(track_currancy)
        self.connections.commit()

    def write_currant_currency(self,currency,rate,date):
        
        clear_table = "DELETE FROM current_currency"
        self.cursor.execute(clear_table)

        for element_num in range(0,len(currency or rate or date)):
            currant_currency = "INSERT INTO current_currency VALUES('{}','{}','{}')".format(currency[element_num],rate[element_num],date[element_num])
            self.cursor.execute(currant_currency)
        self.connections.commit()

    
    def get_all_tracked_user_data(self):
        list_of_data = []
        self.cursor.execute("SELECT * FROM track_currency")
        for row in self.cursor.fetchall():
            list_of_data.append(row)
        return list_of_data

    def tracked_user_data(self,user_id):
        query = "SELECT currency,curr_from,curr_to FROM track_currency WHERE id = '{}'".format(user_id)
        self.cursor.execute(query)
        return [data for data in self.cursor.fetchall()]

    def del_tracked_user(self,user_id):
        query = "DELETE FROM track_currency WHERE id = '{}'".format(user_id)
        self.cursor.execute(query)
        self.connections.commit()


    def update_tracked_user_data(self,user_id,*data):
        query = "UPDATE track_currency SET currency = '{}',curr_from = '{}', curr_to = '{}' WHERE id = '{}'".format(data[0],data[1],data[2],user_id)
        self.cursor.execute(query)
        self.connections.commit()

    def check_tracked_user(self,user_id):
        query = "SELECT EXISTS (SELECT id FROM track_currency WHERE id = '{}')".format(user_id)
        self.cursor.execute(query)
        return [element[0] for element in self.cursor.fetchall()]


    def get_current_data(self):
        curr_data = {}
        self.cursor.execute("SELECT * FROM current_currency")
        for row in self.cursor.fetchall():
            curr_data[row[0]] = row[1]
        return curr_data

