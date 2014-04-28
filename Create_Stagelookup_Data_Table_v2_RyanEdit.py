######################################################################################################################################
# $Id: Create_Stagelookup_Data_Table_v2.py
#
# Project:  Create_Stagelookup_Data_Table (version 2)
# Purpose:  This script can be used to iterate the ESRI ArcMap 3D Analyst Surface Volume tool to 
#                  create a comma delimited text file listing the outputs of the Surface Volume function 
#                  for a Tin or DEM using user-specified increments of surface-water stage (elevation) between 
#                  minimum and maximum values of stage as specified by the user.  It will perform the iteration
#                  through the range of stage values for each land parcel DEM listed in an input text file.
#
#           This script is intended for use in data preparation for the Shoreline Management Tool
#              Snyder, D.T., Haluska, T.L., and Respini-Irwin, D., 2013, 
#              The Shoreline Management Tool - 
#              An ArcMap tool for analyzing water depth, 
#              inundated area, volume, and selected habitats, 
#              with an example for the lower Wood River Valley, Oregon: 
#              U.S. Geological Survey Open-File Report 2012-1247, 86p. 
#              (available at http://pubs.usgs.gov/of/2012/1247.)
#
#           Important Notice: This script has only been minimally tested, is provided "as is," and must be modified for use.
#              Corrections or suggestion are welcome and should be sent to Dan Snyder dtsnyder@usgs.gov
#              Check for updates at http://pubs.usgs.gov/of/2012/1247.
#
#              Data tables containing lookup tables of surface-water stage and the associated volume and area values 
#              must be calculated for each parcel polygon in the land parcel layer.  The data tables consist of 
#              comma-delimited files that should be constructed for each vertical datum required by the user, 
#              such as NAVD88 or NGVD29. The data tables must have values of surface-water stage in feet, 
#              volume of storage in acre-feet, and area of inundation in acres.  
#              The Shoreline Management Tool is currently programmed to look up values within the data tables 
#              with stage increments of 0.01 ft.
#
#              The header line in the first record of the file is used to describe the file and data fields. 
#              For the data part of the file, subsequent records, starting with the second record, contain values of 
#              volume and area for each increment of surface-water stage by parcel. The records for each parcel must be 
#              sorted in the order of increasing surface-water stage. The first field of each data record must be 
#              an integer value representing the parcel number. The second field must be a numeric value of the 
#              surface-water stage in feet for the vertical datum represented by the file. The third field is currently unused.
#              The fourth field is a numeric value of the volume in acre-feet at the specified surface-water stage. 
#              The fifth field is currently unused. The sixth field is a numeric value of the inundated area in acres 
#              for the specified surface-water stage. The remainder of the record should be blank to allow for future options. 
#              Data for subsequent parcels should be appended below the last record for the previous parcel 
#              without repeating the header line used in the first record of the file.
#
#              The required naming convention for the data table files are "StageLookupNAVD88.txt" or "StageLookupNGVD29.txt", 
#              depending on which vertical datum is being used, NAVD88 or NGVD 29, respectively. 
#              The file(s) must be placed in the Tool_Source_Files folder.
#              
#              An example of the output showing the header (which is very long) and two lines is show below.
#                 Input List of DEMs=  E:\Shoreline\ShorelineDirectory\LWRV_5meter_DEM_NAVD88_p27_p31.csv;  Columns=   parc_number,
#                                         refElev_feet,  not_used,  Volume_acft,  not_used,  2D_Area_ac
#                 27,  4140.260000,  not_used,  530.591431,  not_used,  996.295716
#                 27,  4140.270000,  not_used,  540.465780,  not_used,  1002.201601
#
#              Run time depends on DEM resolution, parcel area, number of parcels, stage range, increment level, CPU, and software.
#                 The following run times were obtained using the 56.4 sq. mile (146 sq. km) Lower Wood River Valley, Oregon example
#                 with stage elevations ranging from 4135.30 - 4176.30 feet;
#                 using ArcMap 10.0 SP 5 on a Windows 7 64-bit, processor - Intel Xeon CPU X5570 @ 2.93 GHz, RAM = 3 GB:
#                    Resolution   Increment     Increment iterations for each of 34 land parcels     Total iterations   Total time
#                     1-m DEM      0.10 ft                           411                                  13,974          4.1 hrs
#                     1-m DEM      0.01 ft                          4101                                 139,434         41.9 hrs
#                     5-m DEM      0.10 ft                           411                                  13,974          0.8 hrs
#                     5-m DEM      0.01 ft                          4101                                 139,434          8.2 hrs
#                 Note that it did not appear to take longer if messages were output to the screen for each iteration.
#
######################################################################################################################################
#
# Version      = 2.0
# Version Date = January 23, 2013
# Original Author:  Gerry B. Gabrisch Gerry@gabrisch.us  November 15, 2005
# Modified by       Curtis V. Price   cprice@usgs.gov    January 22, 2013
# Modified by:      Leonard L. Orzol  llorzol@usgs.gov   January 23, 2013
# Modified by:      Daniel T. Snyder  dtsnyder@usgs.gov  January 23, 2013
# Contact:          Daniel T. Snyder  dtsnyder@usgs.gov
#                      U.S. Geological Survey (USGS) Oregon Water Science Center
#                      http://or.water.usgs.gov
#
######################################################################################################################################
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESSED
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
######################################################################################################################################
#
# Issue 1: The following script is used because SurfaceVolume_3d currently (Arc 10.0 SP5) 
#          does not have an option for iteration.
#          An enhancement request has been made to Esri to resolve this issue. 
#
# Issue 2: Because SurfaceVolume_3d currently (Arc 10.0 SP5) outputs the
#          reference plane elevation with only two decimal places of precision it is
#          necessary to take the output from SurfaceVolume_3d and write a separate
#          output file that preserves the full precision of the reference plane volume.
#          An enhancement request has been made to Esri to resolve this issue. 
#
# Assumption 1: The DEM is in elevation units of meters and ground units of meters.
#               Use of a DEM in units other than meters will require modification of the script.
#
# Assumption 2: SurfaceVolume_3d calculates both 2D and 3D areas.
#               2D area is the cumulative area of each cell in the raster projected onto a horizontal datum.
#               3D area is the cumulative area of each cell perpendicular to the slope of the cell.
#               This script is currently written to use 2D area.
#               If 3D area is needed it will require modification of the script.
#
# Warning:    Error messages while running the script might result from previously existing files or directories (though in some
#             instances previously existing directories are required.  To avoid some of these errors this script is designed to 
#             delete or overwrite some existing files.
#
# Suggestion: To save a text file of the screen output while running this script use the following command:
#             Create_Stagelookup_Data_Table_v2.py | tee Create_Stagelookup_Data_Table_v2_output.txt
#             Note that the "|" is the redirect symbol and "tee" will send output to both the screen and the text file.
#
######################################################################################################################################


# Import system modules.
import sys
import os
import time
import arcpy
arcpy.CheckOutExtension("3D") # Check out 3D extension license

starttime = time.clock() 
arcpy.AddMessage("%s" % (""))  #space out screen messages
arcpy.AddMessage("%s %s" % ("Starting  ", time.strftime("%I:%M:%S", time.localtime())))
arcpy.AddMessage("%s" % (""))  #space out screen messages

arcpy.AddMessage("%s" % ("Setting Workspace and settings"))



### *************************************************** USER-DEFINED VARIABLES *******************************************************
### **********************************************************************************************************************************
### **********************************************************************************************************************************
### Begin Setting Variables (***!!!these need to be set by user!!!***)
### This is the only place that generally would need to be modified by the user for their project.
###
###
inDEM_list_path = r"F:\ShorelineDirectory\Tool_Source_Files\Python_Scripts" # String: Path to folder with file of input list of DEMs.
###                                                                         #         Do not include a trailing "\" at end. 
inDEM_list_name = "LWRV_5meter_DEM_NAVD88.csv"                # String: Filename of input list of DEMs. 
###                                                           #        This must be a comma delimited text file with no header line.
###                                                           #        The first field is the integer of the land parcel number; 
###                                                           #           (should = PARC_NUMBER from the Parcels layer).
###                                                           #        The second is the name of the input DEM.
###                                                           #        There should be no additional fields on each record.
###                                                           #        Two lines from the example file inDEM_list_name
###                                                           #            "LWRV_5meter_DEM_NAVD88.csv" are show below:
###                                                           #        9,p9_5mdem88
###                                                           #        10,p10_5mdem88
###
inDEMpath       = r"F:\ShorelineDirectory\GIS_Layers"         # String:  Path to input DEMs.
###                                                           #             Do not include a trailing "\" at end. 

###                                                           #             Do not include a trailing "\" at end. 
inDEMdatum      = "NAVD88"                                    # String:  Vertical datum of input DEMs: NAVD88 or NGVD29.
out_folder_path = r"F:\ShorelineDirectory\Tool_Source_Files"  # String:  Path to output folder for output text file.
###                                                           #             The file(s) must be located in the folder: 
###                                                           #             \ShorelineDirectory\Tool_Source_Files
###                                                           #             Do not include a trailing "\" at end. 
###
startElev_feet  = 4135.30   # Float:   Start elevation level (units in feet)  NOTE: this must be the LOWER elevation value.
endElev_feet    = 4176.30   # Float:   End elevation level   (units in feet)  NOTE: this must be the UPPER elevation value.
incElev_feet    = 0.01      # Float:   Elevation increment to use for iteration (units in feet).
#                           #             Value will be rounded to "numDecimals" set below.
numDecimals     = 2         # Integer: Number of decimals to round feet elevation values.
zFact           = 1.0       # Float:   Z factor: Set to 1.0 if ground and elevation units of DEM are same units (such as meters).
###                         #             See help for SurfaceVolume_3d if DEM ground and elevation units are different.
refPlane        = "BELOW"   # String:  Set to ABOVE or BELOW, see the help for SurfaceVolume_3d.
###                         #             (selects whether to calculate area & volume above or below given reference plane elev).
###
###
### End Setting Variables (user should not normally need to modify script below this point).
### **********************************************************************************************************************************
### **********************************************************************************************************************************
### **********************************************************************************************************************************



# Prepare output file.
outFile_name   = "StageLookup" + inDEMdatum + ".txt"          # Name of output text file of elevation, area, and volume .
#                                                             #    WARNING: will overwrite existing file.
#                                                             # The required naming convention for the data table files are 
#                                                             #    StageLookupNAVD88.txt or StageLookupNGVD29.txt, depending on 
#                                                             #    vertical datum used, NAVD88 or NGVD 29, respectively. 
outFile        = os.path.join(out_folder_path,outFile_name)   # Full path and file name of output file.
# Open listing file.
#
output = open(outFile,"w")

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
   "refElev_feet","not_used","Volume_acft","not_used","2D_Area_ac"))

# Write screen header info with column names (the lines below may be commented out if screen display is not needed).
arcpy.AddMessage("%s" % (""))  #space out screen messages
arcpy.AddMessage("%s" % (""))  #space out screen messages
arcpy.AddMessage("%s" % ("OUTPUT COLUMNS:"))
arcpy.AddMessage("%s, %s, %s, %s, %s, %s" % ("parcel_number","refElev_feet","not_used","Volume_acre-feet","not_used","2D_Area_acres"))

# Round increment to user-specified number of decimals to prevent deviations due to floating point values.
incElev_feet = round(incElev_feet,numDecimals)

# Iterate through all the DEMs in inDEMList.
for aLine in inDEM_list:

    if len(aLine) < 1:
        break
    parc_numSTR, inDEMname = aLine.split( "," )
    inDEM = os.path.join(inDEMpath,inDEMname)
    if parc_numSTR is None or parc_numSTR == "":
        break
    arcpy.AddMessage("%s" % (""))  #space out screen messages
    arcpy.AddMessage("%s" % (""))  #space out screen messages
    arcpy.AddMessage("%s, %s" % ("Parcel Number= " + parc_numSTR,"Input DEM= "+ inDEM))
    parc_number = int(parc_numSTR)


    # Initialize reference plane elevation (in feet) and round to user-specified number of decimals.
    refElev_feet = round(startElev_feet,numDecimals)   # Round to prevent deviations due to using floating point values.
 
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
            arcpy.AddMessage("%i,  %f,  %s,  %f,  %s,  %f" % (parc_number,refElev_feet,"not_used",vol3d_acft,"not_used",area2d_ac))
            # The above line may be commented out if screen display is not needed.
       
            # Write the input and output values to the output file.
            output.write("%i,  %f,  %s,  %f,  %s,  %f\r\n" % (parc_number,refElev_feet,"not_used",vol3d_acft,"not_used",area2d_ac))
        
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
