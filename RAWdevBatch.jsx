//@includepath "./JSON Action Manager/"
//@include "jamEngine.jsxinc"

//@include "jamJSON.jsxinc"

app.preferences.rulerUnits = Units.PIXELS;
app.preferences.typeUnits = TypeUnits.PIXELS;
app.displayDialogs = DialogModes.NO;

var SKIP = true;
var OVERWRITE = false;
var doSkip = SKIP;

var tiffOptions = new TiffSaveOptions();
tiffOptions.embedColorProfile = true;
tiffOptions.annotations = true;

inputFolderName = Folder.selectDialog("Select an INPUT folder");
outputFolderName = Folder.selectDialog("Select an OUTPUT folder");
// inputFolderName = "Volumes/home/Soybean/Tanashi_2016/20160708"
// outputFolderName = "Volumes/home/Soybean/Tanashi_2016_output/20160708"
var inputFolder = new Folder(inputFolderName);
var infoFileName = inputFolderName + "/info.json";
var infoFile = new File(infoFileName);

if (infoFile.exists == false) {
	alert("There is no 'info.json' file in " + infoFileName);
	kill();
}

if (infoFile.open("r") == true){
	infotext = infoFile.read();
	infoFile.close();
}else{
	alert("'info.json' can not be opened.");
	kill();
}

var pathes = new Array();

var jsObj = jamJSON.parse(infotext, true);
for (var key in jsObj){
	var obj = jsObj[key]["path"];
	pathes.push(obj);
}

for (var i = 0; i < pathes.length; i++){
	var absPath = pathes[i].replace("./","");
	var inputParentFolderName = inputFolderName + "/" + absPath;
	var inputParentFolder = new Folder(inputParentFolderName);
	var inputFiles = inputParentFolder.getFiles("*.CR2");
	if (inputFiles.length == 0) {
		alert("There is no RAW(CR2) data in "+ inputParentFolderName);
	}
	for (var j = 0; j < inputFiles.length; j ++) {
		// files 
		var inputFileName = inputFiles[j];
		var inputFile = new File(inputFileName);
		var outputParentFolderName = outputFolderName + "/" + absPath;
		var outputParentFolder = new Folder(outputParentFolderName);
		var outputFileName = outputParentFolderName +"/"+ inputFile.name.substr(0, inputFile.name.length - 4) + ".tif";
		var outputFile = new File(outputFileName)
		var isDupulicated = outputFile.exists;

		if (isDupulicated && doSkip){
			break;
		}

		// input
		var inputDocument = app.open(inputFileName);

		// Checking an existence of a parent directory of output tiff files
		
		
		var isFolder = outputParentFolder.exists;
		if (isFolder == false){
			var isCreated = outputParentFolder.create();
			if (isCreated == false){
				alert("Failed: the folder '' is not created.");
			}
		}

		// Save
		inputDocument.saveAs(outputFile, tiffOptions, true);
		inputDocument.close(SaveOptions.DONOTSAVECHANGES);
		
	}
}