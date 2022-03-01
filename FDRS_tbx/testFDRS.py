import CalculateFWI
import arcpy
import datetime
import numpy as np

def testFDRS():
    temp_ras = arcpy.Raster("S:\\WFP2\\arctoolboxforfdrs\\Temperature\\idn_cli_temperature_fio_2016.01.01.tif")
    temp_nodata = temp_ras.noDataValue
    rh_ras = arcpy.Raster("S:\\WFP2\\arctoolboxforfdrs\\RelativeHumidity\\idn_cli_rh_5km_gfs.2016.01.01.tif")
    wind_ras = arcpy.Raster("S:\\WFP2\\arctoolboxforfdrs\\WindSpeed\\idn_cli_windspeed_5km_gfs.2016.01.01.tif")
    rain_ras = arcpy.Raster("S:\\WFP2\\arctoolboxforfdrs\\Precipitation\\idn_cli_chirps-v2.0.2016.01.01.tif")
    temp_arr = arcpy.RasterToNumPyArray(temp_ras)
    rh_arr = arcpy.RasterToNumPyArray(rh_ras)
    wind_arr = arcpy.RasterToNumPyArray(wind_ras)
    rain_arr = arcpy.RasterToNumPyArray(rain_ras)
    # change Precipitation no-data values to 0
    rain_nodata = rain_ras.noDataValue
    rain_arr[rain_arr == rain_nodata] = 0


        # ffmc_val = parameters[6].valueAsText
        # dmc_val = parameters[7].valueAsText
        # dc_val = parameters[8].valueAsText
        # # create array with values
        # ffmc_prev_arr = np.full(temp_arr.shape, ffmc_val)
        # dmc_prev_arr = np.full(temp_arr.shape, dmc_val)
        # dc_prev_arr = np.full(temp_arr.shape, dc_val)
    ffmc_prev_ras = arcpy.Raster("S:\\WFP2\\arctoolboxforfdrs\\InitialValue\\idn_cli_ffmc_day0_2016.12.31.tif")
    dmc_prev_ras = arcpy.Raster("S:\\WFP2\\arctoolboxforfdrs\\InitialValue\\idn_cli_dmc_day0_2016.12.31.tif")
    dc_prev_ras = arcpy.Raster("S:\\WFP2\\arctoolboxforfdrs\\InitialValue\\idn_cli_dc_day0_2016.12.31.tif")
    ffmc_prev_arr = arcpy.RasterToNumPyArray(ffmc_prev_ras)
    dmc_prev_arr = arcpy.RasterToNumPyArray(dmc_prev_ras)
    dc_prev_arr = arcpy.RasterToNumPyArray(dc_prev_ras)

    # calculate latitude array
    lat_arr = __calcLatitudeArray(temp_ras)
    sdate = datetime.date(2016,01,01)
    # create masked arrays
    temp_ma = np.ma.masked_where(temp_arr == temp_nodata, temp_arr, True)
    rh_ma = np.ma.masked_where(temp_arr == temp_nodata, rh_arr, True)
    wind_ma = np.ma.masked_where(temp_arr == temp_nodata, wind_arr, True)
    ffmc_prev_ma = np.ma.masked_where(temp_arr == temp_nodata, ffmc_prev_arr, True)
    dmc_prev_ma = np.ma.masked_where(temp_arr == temp_nodata, dmc_prev_arr, True)
    dc_prev_ma = np.ma.masked_where(temp_arr == temp_nodata, dc_prev_arr, True)
    fwi, ffmc, dmc, dc, bui, isi = CalculateFWI.calculateFWI(temp_ma, rh_ma, wind_ma, rain_arr, ffmc_prev_ma,
                 dmc_prev_ma, dc_prev_ma, lat_arr, sdate)

    lowerLeft = arcpy.Point(temp_ras.extent.XMin,temp_ras.extent.YMin)
    cellSize = temp_ras.meanCellWidth
    arcpy.env.outputCoordinateSystem = temp_ras
    arcpy.env.cellSize = temp_ras
    arcpy.env.nodata = "PROMOTION"

    newRaster = arcpy.NumPyArrayToRaster(fwi,lowerLeft,cellSize,
                                 value_to_nodata=-99999)
    newRaster.save("S:\\WFP2\\arctoolboxforfdrs\\Output\\src_idn_fwi.2016.01.01.tif")
    newRaster = arcpy.NumPyArrayToRaster(ffmc,lowerLeft,cellSize,
                                 value_to_nodata=-99999)
    newRaster.save("S:\\WFP2\\arctoolboxforfdrs\\Output\\src_idn_ffmc.2016.01.01.tif")
    newRaster = arcpy.NumPyArrayToRaster(dmc,lowerLeft,cellSize,
                                 value_to_nodata=-99999)
    newRaster.save("S:\\WFP2\\arctoolboxforfdrs\\Output\\src_idn_dmc.2016.01.01.tif")
    newRaster = arcpy.NumPyArrayToRaster(dc,lowerLeft,cellSize,
                                 value_to_nodata=-99999)
    newRaster.save("S:\\WFP2\\arctoolboxforfdrs\\Output\\src_idn_dc.2016.01.01.tif")
    newRaster = arcpy.NumPyArrayToRaster(bui,lowerLeft,cellSize,
                                 value_to_nodata=-99999)
    newRaster.save("S:\\WFP2\\arctoolboxforfdrs\\Output\\src_idn_bui.2016.01.01.tif")
    newRaster = arcpy.NumPyArrayToRaster(isi,lowerLeft,cellSize,
                                 value_to_nodata=-99999)
    newRaster.save("S:\\WFP2\\arctoolboxforfdrs\\Output\\src_idn_isi.2016.01.01.tif")

    return

def __calcLatitudeArray(inRaster):
    # import arcgisscripting
    # gp = arcgisscripting.create(9.3)
    # gp.CheckOutExtension("Spatial")
    # gp.WorkSpace = os.path.dirname(inRaster)
    # gp.SingleOutputMapAlgebra_sa(
    #     "Con(IsNull({0}), {1}, $$YMap)".format(inRaster, inRaster),
    #     lat_raster)
    # del gp
    ##Get properties of the input raster
    inRasterDesc = arcpy.Describe(inRaster)

    #coordinates of the lower left corner
    rasXmin = inRaster.extent.XMin
    rasYmin = inRaster.extent.YMin

    # Cell size, raster size
    rasMeanCellHeight = inRaster.meanCellHeight
    rasMeanCellWidth = inRaster.meanCellWidth
    rasHeight = inRaster.height
    rasWidth = inRaster.width
    print ("rasYmin: {0}, rasMeanCellHeight: {1}, rasHeight: {2}, rasWidth: {3}".format(
            rasYmin, rasMeanCellHeight, rasHeight, rasWidth))
    ##Calculate coordinates basing on raster properties
    #create numpy array of coordinates of cell centroids
    def rasCentrY(rasHeight, rasWidth):
        coordY = rasYmin + ((0.5 + rasHeight) * rasMeanCellHeight)
        return coordY
    inRasterCoordY = np.fromfunction(rasCentrY, (rasHeight,rasWidth)) #numpy array of Y coord

    return inRasterCoordY

arcpy.env.overwriteOutput = True
testFDRS()