# Let me help you upload your old bulk data to Firebase

1. Export the Excel file as CSV

2. Use this [tool](https://codebeautify.org/csv-to-xml-json) to convert this CSV to JSON

3. Use a text editor Find-and-Replace to change ```{``` to ```"x": {```. Also remove the ```[]``` in the beginning and ending.

4. Use this Linux command to change each of the ```x``` to incemental numbers

```awk 'BEGIN { cntr = 0 } /"x":/ { cntr++ ; print "\""cntr"\":" } !/header/ { print $0 }' codebeautify.json > output.json```

(Remember this code doesn't do the exact thing for us, so one more step)

5. ```"x":``` is not removed, so to remove it use text editor Find-and-Replace to change ```"x":``` to blank.

6. Last step, but important - convert the encoding of the file to strictly **UTF-8**, nothing else is accepted.

Done! Goto [Firebase Database Console](https://console.firebase.google.com/u/0/project/jlg-ops/database/jlg-ops/data/jlg_main/jlg_execution) and upload the output.json using Import JSON.

_Recommended to use Visual Studio Code for the purpose (especially Step 6)._