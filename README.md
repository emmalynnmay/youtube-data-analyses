# Final Project

CS 5830 - Data Science in Practice

Ann Marie Humble & Emma Lynn May

## Generate a New Dataset 
With current data from the YouTube API!

* Create a python virtual environment:

    `python3 -m venv my_env`

* Activate the virtual environment:

    `source my_env/bin/activate`

* Install required packages:

    `pip3 install -r requirements.txt`

* [Create a YouTube API key](https://developers.google.com/youtube/v3/getting-started)

* Rename the `example.env` file to `.env`. Replace `YOUR-API-KEY-HERE` with your API key.

* Run the script to create the dataset:

    `python3 create-dataset.py`

* To use the new dataset in analysis.ipynb, rename `new-youtube-data.csv` to `youtube-data.csv`

* Deactivate the virtual environment:

    `deactivate`

## References


