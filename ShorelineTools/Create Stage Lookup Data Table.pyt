import arcpy


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Shoreline Management Tool"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [CreateStageLookup]


class CreateStageLookup(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Create Stage Lookup tool"
        self.description = ""
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        
        inDEM_list = arcpy.Parameter(
            displayName ="Input Location of DEM list .txt",
            name = "inDEM_list",
            datatype="DEFile",
            direction="input")

        inDEMpath = arcpy.Parameter(
            displayName ="Folder with DEMs",
            name = "inDEMpath",
            datatype="DEFolder",
            direction="input")
        
        inDEMdatum = arcpy.Parameter(
            displayName ="DEM Datum",
            name = "inDEMdatum",
            datatype="GPString",
            direction="input")
        
        out_folder_path = arcpy.Parameter(
            displayName ="Output folder",
            name = "out_folder_path",
            datatype="DEFolder",
            direction="input")

        startElev_feet = arcpy.Parameter(
            displayName ="Starting elevation",
            name = "startElev_feet",
            datatype="GPString",
            direction="input")

        endElev_feet = arcpy.Parameter(
            displayName ="Ending elevation",
            name = "endElev_feet",
            datatype="GPString",
            direction="input")

        incElev_feet = arcpy.Parameter(
            displayName ="Starting Elevation",
            name = "incElev_feet",
            datatype="GPString",
            direction="input")
        
        numDecimals = arcpy.Parameter(
            displayName ="Number of decimals",
            name = "numDecimals",
            datatype="GPString",
            direction="input")        
    
        zFact = arcpy.Parameter(
            displayName ="Z factor",
            name = "zFact",
            datatype="GPString",
            direction="input")
        
        refPlane = arcpy.Parameter(
            displayName ="Reference plane",
            name = "refPlane",
            datatype="GPString",
            direction="input")

        params = [inDEM_list, inDEMpath, inDEMdatum, out_folder_path, startElev_feet, endElev_feet, incElev_feet, numDecimals, zFact, refPlane]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        
        refPlane_list = ["ABOVE", "BELOW"]


        #
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        
        inDEM_list = arcpy.GetParameterAsText(0)
        inDEMpath = arcpy.GetParameterAsText(1)
        inDEMdatum = arcpy.GetParameterAsText(2)

        out_folder_path = arcpy.GetParameterAsText(3)   

        startElev_feet = float(arcpy.GetParameterAsText(4))
        endElev_feet = float(arcpy.GetParameterAsText(5))   
        incElev_feet = float(arcpy.GetParameterAsText(6))                           
        numDecimals = int(arcpy.GetParameterAsText(7))        
        zFact = float(arcpy.GetParameterAsText(8))
        refPlane = arcpy.GetParameterAsText(9) 

        # Prepare output file.
        # RYAN COMMENT - Put check to see if file exists in folder.
        outFile_name   = "StageLookup" + inDEMdatum + "_test1.txt"          # Name of output text file of elevation, area, and volume .
        #                                                             #    WARNING: will overwrite existing file.
        #                                                             # The required naming convention for the data table files are 
        #                                                             #    StageLookupNAVD88.txt or StageLookupNGVD29.txt, depending on 
        #                                                             #    vertical datum used, NAVD88 or NGVD 29, respectively. 
        outFile        = os.path.join(out_folder_path,outFile_name)   # Full path and file name of output file.
        # Open listing file.
        #
        output = open(outFile,"w")


        # Split path DEM b
        inDEM_list_path = os.path.dirname(inDEM_list)
        inDEM_list_name = os.path.basename(inDEM_list) #takes filename from the HOLV path


        # Check file.
        #
        if output is None:
           arcpy.AddMessage("%s %s" % ("Error: Unable to open output file ",output_file))
           sys.exit( 1 )

        # Write to screen the parameters specified for the run.
        arcpy.AddMessage("%s" % (""))  #space out screen messages
        arcpy.AddMessage("%s" % (""))  #space out screen messages
        arcpy.AddMessage("%s" % ("USER-SPECIFIED INPUT PARAMETERS:"))
        arcpy.AddMessage("%s %s" % ("   Path to folder with file of input list of DEMs (inDEM_list_path)     =", inDEM_list_path))
        arcpy.AddMessage("%s %s" % ("   Filename of input list of DEMs                 (inDEM_list_name)     =", inDEM_list_name))
        arcpy.AddMessage("%s %s" % ("   Path to input DEMs                             (inDEMpath)           =", inDEMpath))
        arcpy.AddMessage("%s %s" % ("   Vertical datum of input DEMs: NAVD88 or NGVD29 (inDEMdatum)          =", inDEMdatum))
        arcpy.AddMessage("%s %s" % ("   Path to output folder for output text file     (out_folder_path)     =", out_folder_path))
        arcpy.AddMessage("%s" % (""))  #space out screen messages
        arcpy.AddMessage("%s %f" % ("   Starting Elevation, in ft          (startElev_feet) =", startElev_feet))
        arcpy.AddMessage("%s %f" % ("   Ending   Elevation, in ft          (endElev_feet)   =", endElev_feet))
        arcpy.AddMessage("%s %f" % ("   Increment, in ft                   (incElev_feet)   =", incElev_feet))
        arcpy.AddMessage("%s %i" % ("   Num. decimals to round elev, in ft (numDecimals)    =", numDecimals))
        arcpy.AddMessage("%s %f" % ("   Z-Factor                           (zFact)          =", zFact))
        arcpy.AddMessage("%s %s" % ("   Reference Plane                    (refPlane)       =", refPlane))
        arcpy.AddMessage("%s" % (""))  #space out screen messages

        inDEM_list_fullpath  = os.path.join(inDEM_list_path,inDEM_list_name)
        arcpy.AddMessage("%s %s" % ("   Full path and filename of input list of DEMs (inDEM_list_fullpath) =", inDEM_list_fullpath))
        arcpy.AddMessage("%s" % (""))  #space out screen messages
        inDEM_list       = file(inDEM_list_fullpath, "r" )

        arcpy.AddMessage("%s" % (""))  #space out screen messages
        arcpy.AddMessage("%s %s" % ("Output file location:", outFile))   # Print output file location to screen.
        arcpy.AddMessage("%s" % (""))  #space out screen messages

        # Write output file header info with column names.
        output.write("%s%s%s  %s,  %s,  %s,  %s,  %s,  %s\r\n" % ("Input DEM list=  ",inDEM_list_fullpath,";  Columns= ","parc_number",\
          "refElev_feet","not_used", "not_used", "Volume_acft", "2D_Area_ac"))

        # output.write("%s%s%s  %s,  %s,  %s,  %s,  %s,  %s\r\n" % ("Input DEM list=  ",inDEM_list_fullpath,";  Columns= ","parc_number",\
        #    "refElev_feet","not_used",  "Volume_acft", "not_used", "2D_Area_ac"))

        # Write screen header info with column names (the lines below may be commented out if screen display is not needed).
        arcpy.AddMessage("%s" % (""))  #space out screen messages
        arcpy.AddMessage("%s" % (""))  #space out screen messages
        arcpy.AddMessage("%s" % ("OUTPUT COLUMNS:"))
        arcpy.AddMessage("%s, %s, %s, %s, %s, %s" % ("parcel_number","refElev_feet","not_used","not_used", "Volume_acre-feet","2D_Area_acres")) #RYAN switch 4th & 5th column
        # arcpy.AddMessage("%s, %s, %s, %s, %s, %s" % ("parcel_number","refElev_feet","not_used","Volume_acre-feet","not_used","2D_Area_acres"))

        # Round increment to user-specified number of decimals to prevent deviations due to floating point values.
        incElev_feet = round(incElev_feet,numDecimals)

        # Iterate through all the DEMs in inDEMList.
        for aLine in inDEM_list:

            if len(aLine) < 1:
                break
            parc_numSTR, inDEMname = aLine.split( "," )
            inDEM = os.path.join(inDEMpath,inDEMname)
            if parc_numSTR is None or parc_numSTR == "":
                #arcpy.AddMessage("this is what happened") #RYAN EDIT
                break
            arcpy.AddMessage("")  #space out screen messages
            arcpy.AddMessage("")  #space out screen messages
            arcpy.AddMessage("%s, %s" % ("Parcel Number= " + parc_numSTR,"Input DEM= "+ inDEM))
            parc_number = int(parc_numSTR)


            # Initialize reference plane elevation (in feet) and round to user-specified number of decimals.
            refElev_feet = round(startElev_feet,numDecimals)   # Round to prevent deviations due to using floating point values.
            arcpy.AddMessage("Rounded to prevent deviations") #RYAN Add for testing
            # Loop through elevations incrementally to calculate area and volume, writing results to screen and text file.
            #
            try:
                # Return a new output for every change of incElev elevation unit.
                # SurfaceVolume appends data if the file exists already.
                #
                while refElev_feet <= endElev_feet:
                    refElev_meters = refElev_feet/3.280833        # Reference plane elevation converted to meters.
                    #
                    arcpy.env.overwriteOutput = True              # Needed to append each new record to the output file.

                    # Run the SurfaceVolume_3d program with the user-defined values.
                    #
                    arcpy.SurfaceVolume_3d(inDEM, "", refPlane, refElev_meters, zFact)

                    # Obtain the values or 2D Area, 3D Area, and Volume reported by SurfaceVolume_3d
                    #    by searching through the output message results string.
                    #
                    r = arcpy.GetMessage(2)
                    area2d_m2 = float(r[r.find("2D Area=") + 8:r.find("3D Area=")])
                    area3d_m2 = float(r[r.find("3D Area=") + 8:r.find("Volume=")])
                    vol3d_m3  = float(r[r.find("Volume=")+7:])

                    # Convert from units of square meters and cubic meters to acres and acre-ft, respectively
                    area2d_ac    = area2d_m2 / 4046.873
                    area3d_ac    = area3d_m2 / 4046.873
                    vol3d_acft   = vol3d_m3  / 1233.489
             
                    # Report the input and output values to the screen.

                    arcpy.AddMessage("%i,  %f,  %s,  %s,  %f,  %f" % (parc_number,refElev_feet,"not_used","not_used",vol3d_acft,area2d_ac)) # RYAN fix, switch 4th & 5th columns
                    #arcpy.AddMessage("%i,  %f,  %s,  %f,  %s,  %f" % (parc_number,refElev_feet,"not_used",vol3d_acft,"not_used",area2d_ac))
                    # The above line may be commented out if screen display is not needed.
               
                    # Write the input and output values to the output file.

                    #RYAN COMMENT. Correct output (from top): parc_number, refElev_feet,  not_used,  Volume_acft,  not_used,  2D_Area_ac 
                    output.write("%i,  %f,  %s,  %s,  %f,  %f\r\n" % (parc_number,refElev_feet,"not_used", "not_used", vol3d_acft,area2d_ac))
                
                    # Increment the refPlane elevation and loop and round to user-specified number of decimals
                    refElev_feet = round(refElev_feet + incElev_feet,numDecimals) # Round to avoid deviations due to floating point values.

            except Exception, msg:
                arcpy.AddMessage(str(msg))

        # Close files.
        inDEM_list.close()
        output.close()

        arcpy.AddMessage("%s" % (""))  #space out screen messages
        arcpy.AddMessage("%s" % (""))  #space out screen messages
        arcpy.AddMessage("%s" % (""))  #space out screen messages
        stoptime = time.clock() 
        arcpy.AddMessage("%s %s" % ("DONE:  ", time.strftime("%I:%M:%S", time.localtime())))
        arcpy.AddMessage("%s" % (""))  #space out screen messages
        arcpy.AddMessage("%s %s" % ("Output file location  =", outFile))
        arcpy.AddMessage("%s" % (""))  #space out screen messages
        arcpy.AddMessage("%s %.1f" % ("Elapsed time in minutes: ", ((stoptime-starttime)/60)))