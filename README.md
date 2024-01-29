# Flash50
### Application Website: https://mostafaayman.pythonanywhere.com
### Video Demo:  https://youtu.be/rR2cQlJqE4k
### Description
* This is my final project for CS50x 2023.

* Flash50 is a web application created using HTML, CSS, SQLITE & Python's Flask Framework.

### Concept
* The idea of the application is that it allows users to create collections of flash cards.

* This can be useful for pretty much anyone, as flash cards have proved to be a popular method for memorizing study materials, which is handy for university students, school students, or even software engineers.

### Future Improvements
* Designing a better front-end that's responsive and not plain like the current one.

* Allowing the flash card content to include images or videos or blocks of code.

* Whenever a new collection is created, the user has the option of making it private (only available to him) or making it public which allows all the other users to view and download this collection.
  
### Installation
1. Make sure that Python is installed on your local machine, preferably version 3.10 or higher.
2. Download all the files inside a local folder on your machine.
3. Install with pip after running a bash window inside the directory.
   
   ```
   $ pip install -r requirements.txt
   ```
4. Run app.py
   
### Notes
* When testing either locally or on the website, you can use a test user that's already in the database. ==> Username: test  | Password: 123
* To view the content of the card inside a collection, simply click on the notebook that is hiding the card's content to make it disappear.
* The collection name has a maximum letter count of 6, while the title of any card has a maximum letter count of 12.