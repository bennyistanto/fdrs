import arcpy
import numpy as np
np.set_printoptions(threshold=np.inf)
import math
import datetime
import os
import CalculateFWI

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [FDRS]


class FDRS(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Fire Danger Rating System"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        # MONTH,TEMP,RH,WIND,RAIN,FFMCPrev,DMCPrev,DCPrev,LAT

        # Parameter - MONTH
        param0 = arcpy.Parameter(
            displayName="Month",
            name="in_month",
            datatype="GPDate",
            parameterType="Required",
            direction="Input"
        )
#        param0.filter.type = "Range"
#        param0.filter.list = [1, 12]

        # Parameter - TEMP
        param1 = arcpy.Parameter(
            displayName="Temperature",
            name="in_temp",
            datatype=["GPRasterLayer"],
            parameterType="Required",
            direction="Input"
        )


        # Parameter - RH
        param2 = arcpy.Parameter(
            displayName="Relative Humidity",
            name="in_rh",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input"
        )

        # Parameter - WIND
        param3 = arcpy.Parameter(
            displayName="Wind",
            name="in_wind",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input"
        )

        # Parameter - RAIN
        param4 = arcpy.Parameter(
            displayName="Rainfall",
            name="in_rain",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input"
        )

        # Parameter - Initial values from file?
        param5 = arcpy.Parameter(
            displayName="Use initial value",
            name="in_init_values",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input",
        )
#        param5.filter.type = "ValueList"
#        param5.filter.list = ["USE_INITIAL_VALUE", "RECEIVE_FROM_FILE"]

        # Parameter - FFMCPrev (value)
        param6 = arcpy.Parameter(
            displayName="Previous FFMC value",
            name="in_ffmc_val",
            datatype=["GPLong"],
            parameterType="Required",
            direction="Input"
        )
        param6.value = 85

        # Parameter - DMCPrev (value)
        param7 = arcpy.Parameter(
            displayName="Previous DMC value",
            name="in_dmc_val",
            datatype=["GPLong"],
            parameterType="Required",
            direction="Input"
        )
        param7.value = 6

        # Parameter - DCPrev (value)
        param8 = arcpy.Parameter(
            displayName="Previous DC value",
            name="in_dc_val",
            datatype=["GPLong"],
            parameterType="Required",
            direction="Input"
        )
        param8.value = 15

        # Parameter - FFMCPrev (file)
        param9 = arcpy.Parameter(
            displayName="Previous FFMC layer",
            name="in_ffmc_file",
            datatype=["GPRasterLayer"],
            parameterType="Optional",
            direction="Input"
        )

        # Parameter - DMCPrev (file)
        param10 = arcpy.Parameter(
            displayName="Previous DMC layer",
            name="in_dmc_file",
            datatype=["GPRasterLayer"],
            parameterType="Optional",
            direction="Input"
        )

        # Parameter - DCPrev (file)
        param11 = arcpy.Parameter(
            displayName="Previous DC layer",
            name="in_dc_file",
            datatype=["GPRasterLayer"],
            parameterType="Optional",
            direction="Input"
        )

        # Parameter - Output FWI
        param12 = arcpy.Parameter(
            displayName="Fire Weather Index",
            name="out_fwi",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Output"
        )

        # Parameter - Output FFMC
        param13 = arcpy.Parameter(
            displayName="FFMC",
            name="out_ffmc",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Output"
        )

        # Parameter - Output DMC
        param14 = arcpy.Parameter(
            displayName="DMC",
            name="out_dmc",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Output"
        )

        # Parameter - Output DC
        param15 = arcpy.Parameter(
            displayName="DC",
            name="out_dc",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Output"
        )

        # Parameter - Output BUI
        param16 = arcpy.Parameter(
            displayName="BUI",
            name="out_bui",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Output"
        )

        # Parameter - Output ISI
        param17 = arcpy.Parameter(
            displayName="ISI",
            name="out_isi",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Output"
        )

        # Parameter - Output DSR
        param18 = arcpy.Parameter(
            displayName="DSR",
            name="out_dsr",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Output"
        )
        param5.value = True
        param6.enabled = False
        param8.enabled = False
        param10.enabled = False
        param7.enabled = False

        params = [param0, param1, param2, param3, param4, param5, param6, param7, param8,
                  param9, param10, param11, param12, param13, param14, param15, param16,
                  param17, param18]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        # param [0,1,2,3,4,boolean,in_ffmc_prev_val, in_dmc_prev_val, in_dc_prev_val,
        #        in_ffmc_prev_file, in_dmc_prev_file, in_dc_prev_file, 12, 13, 14, 15, 16, 17, 18]
        if not parameters[5].hasBeenValidated:
            if parameters[5].value == True: # use initial value
                parameters[6].enabled = True
                parameters[7].enabled = True
                parameters[8].enabled = True
                parameters[9].enabled = False
                parameters[10].enabled = False
                parameters[11].enabled = False
            else:
                parameters[6].enabled = False
                parameters[7].enabled = False
                parameters[8].enabled = False
                parameters[9].enabled = True
                parameters[10].enabled = True
                parameters[11].enabled = True

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

#        temp_ras = parameters[1].valueAsText
        temp_ras = arcpy.Raster(parameters[1].valueAsText)
        temp_nodata = temp_ras.noDataValue
        rh_ras = arcpy.Raster(parameters[2].valueAsText)
        wind_ras = arcpy.Raster(parameters[3].valueAsText)
        rain_ras = arcpy.Raster(parameters[4].valueAsText)

        temp_arr = arcpy.RasterToNumPyArray(temp_ras)
        rh_arr = arcpy.RasterToNumPyArray(rh_ras)
        wind_arr = arcpy.RasterToNumPyArray(wind_ras)
        rain_arr = arcpy.RasterToNumPyArray(rain_ras)
        # change Precipitation no-data values to 0
        rain_nodata = rain_ras.noDataValue
        rain_arr[rain_arr == rain_nodata] = 0

        if parameters[5]:
            # use values not files
            ffmc_val = parameters[6].valueAsText
            dmc_val = parameters[7].valueAsText
            dc_val = parameters[8].valueAsText
            # create array with values
            ffmc_prev_arr = np.full(temp_arr.shape, ffmc_val)
            dmc_prev_arr = np.full(temp_arr.shape, dmc_val)
            dc_prev_arr = np.full(temp_arr.shape, dc_val)
        else:
            ffmc_prev_ras = arcpy.Raster(parameters[9].valueAsText)
            dmc_prev_ras = arcpy.Raster(parameters[10].valueAsText)
            dc_prev_ras = arcpy.Raster(parameters[11].valueAsText)
            ffmc_prev_arr = arcpy.RasterToNumPyArray(ffmc_prev_ras)
            dmc_prev_arr = arcpy.RasterToNumPyArray(dmc_prev_ras)
            dc_prev_arr = arcpy.RasterToNumPyArray(dc_prev_ras)

        # calculate latitude array
        lat_arr = self.__calcLatitudeArray(temp_ras)
        mdate = parameters[0].valueAsText
        sdate = datetime.datetime.strptime(mdate, "%d/%m/%Y").date()
#        arcpy.AddMessage("Date: {}".format(mdate))
#        sdate = datetime.date(2016,01,01)
        arcpy.AddMessage("Calculating FWI, FFMC, DMC, DC, BUI and ISI.")
        # create masked arrays
        temp_ma = np.ma.masked_where(temp_arr == temp_nodata, temp_arr, True)
        rh_ma = np.ma.masked_where(temp_arr == temp_nodata, rh_arr, True)
        wind_ma = np.ma.masked_where(temp_arr == temp_nodata, wind_arr, True)
        ffmc_prev_ma = np.ma.masked_where(temp_arr == temp_nodata, ffmc_prev_arr, True)
        dmc_prev_ma = np.ma.masked_where(temp_arr == temp_nodata, dmc_prev_arr, True)
        dc_prev_ma = np.ma.masked_where(temp_arr == temp_nodata, dc_prev_arr, True)

        fwi, ffmc, dmc, dc, bui, isi = CalculateFWI.calculateFWI(temp_ma, rh_ma, wind_ma, rain_arr, ffmc_prev_ma,
                     dmc_prev_ma, dc_prev_ma, lat_arr, sdate)
#        arcpy.AddMessage("fwi:\n {0}".format(fwi[0:2]))
#        arcpy.AddMessage("dc:\n {0}".format(dc[0:2]))
        lowerLeft = arcpy.Point(temp_ras.extent.XMin,temp_ras.extent.YMin)
        cellSize = temp_ras.meanCellWidth

        arcpy.env.outputCoordinateSystem = temp_ras
        arcpy.env.cellSize = temp_ras
        arcpy.env.nodata = "PROMOTION"

        newRaster = arcpy.NumPyArrayToRaster(fwi,lowerLeft,cellSize,
                                     value_to_nodata=-99999)
        newRaster.save(parameters[12].valueAsText)
        newRaster = arcpy.NumPyArrayToRaster(ffmc,lowerLeft,cellSize,
                                     value_to_nodata=-99999)
        newRaster.save(parameters[13].valueAsText)
        newRaster = arcpy.NumPyArrayToRaster(dmc,lowerLeft,cellSize,
                                     value_to_nodata=-99999)
        newRaster.save(parameters[14].valueAsText)
        newRaster = arcpy.NumPyArrayToRaster(dc,lowerLeft,cellSize,
                                     value_to_nodata=-99999)
        newRaster.save(parameters[15].valueAsText)
        newRaster = arcpy.NumPyArrayToRaster(bui,lowerLeft,cellSize,
                                     value_to_nodata=-99999)
        newRaster.save(parameters[16].valueAsText)
        newRaster = arcpy.NumPyArrayToRaster(isi,lowerLeft,cellSize,
                                     value_to_nodata=-99999)
        newRaster.save(parameters[17].valueAsText)

        return

    def __calcLatitudeArray(self, inRaster):

        #coordinates of the lower left corner
        rasXmin = inRaster.extent.XMin
        rasYmin = inRaster.extent.YMin

        # Cell size, raster size
        rasMeanCellHeight = inRaster.meanCellHeight
        rasMeanCellWidth = inRaster.meanCellWidth
        rasHeight = inRaster.height
        rasWidth = inRaster.width
#        arcpy.AddMessage("rasYmin: {0}, rasMeanCellHeight: {1}, rasHeight: {2}, rasWidth: {3}".format(
#            rasYmin, rasMeanCellHeight, rasHeight, rasWidth))
        ##Calculate coordinates basing on raster properties
        #create numpy array of coordinates of cell centroids
        def rasCentrY(rasHeight, rasWidth):
            coordY = rasYmin + ((0.5 + rasHeight) * rasMeanCellHeight)
            return coordY
        inRasterCoordY = np.fromfunction(rasCentrY, (rasHeight,rasWidth)) #numpy array of Y coord

        return inRasterCoordY

