# Timeline Screenshots Generator For Ad Tests

### This script take mp4 files as input and will take screenshots at equal intervals and generate a combine image which can be used in the Ad Test reports.

## Version 2.0
Version Note: In this version the black screen will be filtered out from the screenshots.

## Usage
1. Upload mp4 files of the advert to the "videos" folder
2. Open RUN_screenshots.ipynb
3. Run the code in the first cell (Shift + Enter) to install the packages (only need to do once after starting the notebook )
4. Update the code in the second cell:
	```! python take_screenshots.py "FILENAME.mp4" "NUMBER_OF_FRAME_TAKEN"```
5. Run the code in the second cell
6. Download the generated screenshots from the "screenshots_combined" folder