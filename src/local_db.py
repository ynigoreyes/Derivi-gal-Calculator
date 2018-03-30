from os import chdir, mkdir, listdir, getcwd, path, stat
from abc import abstractclassmethod
from sys import exit
import json
import random


class LOCAL_DB():

  def __init__(self, db_name, table_name):
    # Cache for the database and home directories for ease in navigation
    self.database_dir = path.normpath(getcwd() + '/database')
    self.home_dir = path.normpath(getcwd())

    self.db_name = db_name          # This is the name of the database directory
    self.table_name = table_name    # This is the name of the table in the directory
    self.errorMessage = None        # This is an error message we can pass to the user
    self.connected = False          # This is our connection status
    self.fetch = []                 # This is a list of items that we find

    self.table_columns = []         # Variable used to store the
                    								# columns of each db instance
    self.insertObj = {}             # Used in the insert method
                    								# Creates a dictionary to dump into the table

    if 'database' not in listdir(): # Makes sure the database does not exist yet
      print('creating database for the first time')
      mkdir(self.database_dir)    	# Makes the database dir if it does not exist

    self.__connect(self.table_name) # Creates a the table within the database directory

  def createColumns(self, *args):
    """
    Associates the table column names wiht the table name
    """
    for data in args:
      self.table_columns.append(str(data))

  def __connect(self, table_name):
    """
    Private Method

    Creates a table/collection in the database directory
    """

    chdir(self.database_dir)

    with open(table_name + ".json", "a"):
        print('connecting to table "{}"...'.format(table_name))

    self.connected = True
    chdir(self.home_dir)

  def insert(self, strings):
    """
    @param strings:
    A 2-D Array of strings
    Each row is an "entry"
    Each column in that row is an element.

    If the user does not match the number of columns declared...

    To many values passed: Ignore the last user input
    To little input: the last column decalred does not get a value

    Either way, the entry will always have an Unique ID

    "id": [
      {
        "key": "value"},
      {
        "key": "value"
      },
      {
        "key": "value"
      },
      {
        "key": "value"
      },
      {
        "key": "value"
      },
    ]
    """
    uniqueID = self.generateID()

    tempDict = dict()
    tempList = []

    chdir(self.database_dir)
    if stat(self.table_name + ".json").st_size != 0:

      initJson = open(self.table_name + ".json", "r")
      data = json.load(initJson)
      self.insertObj = data
      initJson.close()

      initJson = open(self.table_name + ".json", "w+")
      initJson.close()

    with open(self.table_name + ".json", "a") as table:
      for index, i in enumerate(strings):

        for key, value in zip(self.table_columns, strings[index]):
          tempDict[key] = value
          tempList.append(tempDict)
          tempDict = {}

        self.insertObj[str(next(uniqueID))] = tempList

        if index == len(strings) - 1:
          json.dump(self.insertObj, table, indent=4)
          # CHANGE WAS MADE: took out sort_keys=True

        tempList = []

    chdir(self.home_dir)

  def remove(self, value, key, howMany="all"):
    """
    we will be looking fo the key that has the...

    "value" in the column "key" and will delete "howMany" entries

    If the user does not pass a howMany variable, we will default
    to deleting all of them.

    TODO: DRY this method up. It works, but will
    be very hard to maintain in the future. This function looks very ugly...

    """

    keyToDelete = None

    if howMany == "all":
      # If the user did not pass a value into howMany, we will delete all
      # entries with that match the criteria
      howMany = True
      pass

    chdir(self.database_dir)

    # This is the json object we will be using
    data = json.load(open(self.table_name + ".json"))

    wantedColumn = self.__getColumnNumber(key)

    if type(howMany) == int:
			# If the user wnats a certain amount of entries to be removed
      for i in range(howMany):

				# This is where we will check to see if the key is found
        for keys in data.keys():
          if value == data[keys][wantedColumn][key]:
            keyToDelete = keys
            break
        if keyToDelete is None:
					# If we did not find a key to delete in the for loop above...
          break
        else:
          try:
            del data[keyToDelete]

            with open(self.table_name + ".json", "w+") as openJson:
              json.dump(data, openJson, indent=4)

          except:
            break

    else:
      while howMany is True:
        for keys in data.keys():
          if value == data[keys][wantedColumn][key]:
            keyToDelete = keys
            break
        if keyToDelete is None:
          break
        else:
          try:
            del data[keyToDelete]

            with open(self.table_name + ".json", "w+") as openJson:
              json.dump(data, openJson, indent=4)

          except:
            break
    chdir(self.home_dir)

  def select(self, targetValue, targetColumn, selectColumn):
    """
    Finds the selectColumn value of the targetValue in the targetColumn

    In relation to common SQL scripts...

    SELECT <selectColumn> FROM self.table_name
    WHERE <targetColumn> is <targetValue>

    Will save the results in the self.fetch list for processing when the
    user calls the fetch method, which then returns the amount of requested
    results.
    """
    self.fetch = []

    targetColumnNumber = self.__getColumnNumber(targetColumn)
    selectColumnNumber = self.__getColumnNumber(selectColumn)

    # Search begins
    # Changes to the database directory
    chdir(self.database_dir)
    data = json.load(open(self.table_name + ".json"))

    if targetColumnNumber is not None and selectColumnNumber is not None:
      for keys in data.keys(): # Goes through the UUID's
        # The variable we are going to save into the list if there is a match
        if targetValue == data[keys][targetColumnNumber][targetColumn]:
          self.fetch.append(data[keys][selectColumnNumber][selectColumn])
    else:
      # This means that there was no columns found
      # with that name or that there were no matching values
      pass

    chdir(self.home_dir)

  def selectAny(self, targetColumn):
    """
    @param string(targetColumn): a string that is the name of a column within the table

    This is what we will use if we want to just find all of a certain column

    @return: None
    """
    self.fetch = []
    targetColumnNumber = self.__getColumnNumber(targetColumn)

    # Changes to the database directory
    chdir(self.database_dir)
    if stat(self.table_name + ".json").st_size != 0:
      data = json.load(open(self.table_name + ".json"))

      # Goes through the keys and saves all of the values in that column
      for keys in data.keys():
        self.fetch.append(data[keys][targetColumnNumber][targetColumn])
    else:
      print("Empty File")

    chdir(self.home_dir)

  def replace(self, targetValue, targetColumn, selectColumn, replaceValue):
    """
    @param targetColumn:
    The column we want to reference
    @param targetValue:
    The value the targetColumn needs to have

    @param selectColumn:
    The column we are going to update
    @param updateValue:
    The value we are going to replace the selectColumn with

    Replace a column in the table where ther targetColumn and targetValue are going to match.
    """

    targetColumnNumber = self.__getColumnNumber(targetColumn)
    selectColumnNumber = self.__getColumnNumber(selectColumn)

    print(targetColumnNumber, selectColumnNumber)

    if targetColumnNumber is None or selectColumnNumber is None:
      print("LOCAL_DB_ERROR: No Columns found to update")
      quit()

    chdir(self.database_dir)

    data = json.load(open(self.table_name + ".json"))
    for keys in data.keys():
      temp = data[keys][targetColumnNumber][targetColumn]
      print(data[keys][targetColumnNumber][targetColumn])
      if targetValue == temp:
        data[keys][selectColumnNumber][selectColumn] = replaceValue
        print(data)
        with open(self.table_name + ".json", "w+") as table:
          json.dump(data, table, indent=4)

    chdir(self.home_dir)

  def update(self, targetValue, targetColumn, selectColumn, updateValue):
    """
    @param targetColumn:
    The column we want to reference
    @param targetValue:
    The value the targetColumn needs to have

    @param selectColumn:
    The column we are going to update
    @param updateValue:
    The value we are going to replace the selectColumn with

    Update a column in the table where ther targetColumn and targetValue are going to match.
    """

    targetColumnNumber = self.__getColumnNumber(targetColumn)
    selectColumnNumber = self.__getColumnNumber(selectColumn)

    if targetColumnNumber is None or selectColumnNumber is None:
      print("LOCAL_DB_ERROR: No Columns found to update")
      quit()

    if targetColumn == selectColumn:
      print("LOCAL_DB_ERROR: targetValue and selectValue cannot be the same")
      quit()

    chdir(self.database_dir)
    updateColumnList = []

    data = json.load(open(self.table_name + ".json"))
    for keys in data.keys():
      temp = data[keys][targetColumnNumber][targetColumn]
      if targetValue == temp:
        print("found a column")
        valueToUpdate = data[keys][selectColumnNumber][selectColumn]
        if valueToUpdate is None:
          valueToUpdate = []
        elif isinstance(valueToUpdate, list) is False: # If it the value found is not a list
          valueToUpdate = [valueToUpdate]

        valueToUpdate.append(updateValue)
        data[keys][selectColumnNumber][selectColumn] = valueToUpdate
        print(data)

        with open(self.table_name + ".json", "w+") as table:
          json.dump(data, table, indent=4)

        # Stop looking for columns to update
        break

    chdir(self.home_dir)

  def fetchResults(self, amount=0):
    """
    @param int(amount): The amount of results the user would like to fetch

    This is how the user will ask for what we were able to find

    @return fetch: If amount was not given or still equals 0, then we will
    return all results found. If there is an int value, associated with amount,
    we will return that amount of results to the user a list
    """
    fetch = []

    if amount == 0:
      fetch = self.fetch
    else:
      fetch = self.fetch[0:amount]

    self.fetch = []
    return fetch

  def __getColumnNumber(self, wantedColumn):
    """
    Private Method

    In order for the column to be referenced within the search functions,
    a number is needed to represent the columns since the collection is a
    list of dictionaries
    """
    for columnNumbers, columnNames in enumerate(self.table_columns):
      if columnNames == wantedColumn:
        return columnNumbers

  def generateID(self):
    seed = random.getrandbits(64)
    while True:
      yield seed
      seed += 1

