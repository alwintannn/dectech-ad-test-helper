# Dectech Ad Test Report Helper

This is Streamlit app containing the following components:

1. Radial Bar Chart Processing
This script takes the overall ad test radial bar chart as an input and generates 4 charts with a different focus for each section using the Dectech Blur.

2. Storyboard Generator
This script take mp4 files as input and will take screenshots at equal intervals and generate a combine image which can be used in the Ad Test reports.

## How to run this app

### Option 1: Install locally using requirements.txt
The app requires Python 3.7. **I'd would be easier to create a new virtual environment**, then running:

```{sh}
git clone https://github.com/presstofan/dectech-ad-test-helper.git
cd dectech-ad-test-helper
pip install -r requirements.txt
streamlit run app.py
```

Some users may experience issues when importing `Shapely`. If that happens to you, the best way to fix it is to switch to `conda`:

```{sh}
pip uninstall shapely
conda install -c conda-forge shapely
```
### Option 2: Run Docker image
Alternatively, please check out the [Docker image](https://hub.docker.com/repository/docker/presstofan/dt-ad-test-helper).

### Option 3: Access via Streamlit Share
The app is temporarily available at [Streamlit Share]( https://share.streamlit.io/presstofan/dectech-ad-test-helper/app.py)