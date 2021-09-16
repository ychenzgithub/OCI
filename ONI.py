import streamlit as st
import pandas as pd
import numpy as np

@st.cache
def getONI():
    import pandas as pd
    import numpy as np

    url = 'http://origin.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_v5.php'
    dfs = pd.read_html(url)          # return a list of DataFrames
    dfONI = dfs[8]                   # extract the correct dataframe
    dfONI = dfONI[dfONI[0]!='Year']  # drop rows that are not good
    dfONI.set_index(0,inplace=True)  # set index using year column
    dfONI.index.rename('Year',inplace=True)  # set index name as 'Year'
    dfONI = dfONI.astype('float')    # turn string data to float

    yst,yed = np.int(dfONI.index.min()),np.int(dfONI.index.max())
    nyr = yed-yst+1
    ONIts = pd.Series(np.zeros(nyr*12)-99,index=pd.period_range(start=str(yst)+'-01-01',end=str(yed)+'-12-01',freq='M'))
    for y in range(yst,yed+1):
        for m in range(1,13):
            vONI = dfONI[m][str(y)]
            ONIts[str(y)+'-'+str(m)] = vONI
    ONIts.dropna(inplace=True)
    return ONIts

def getAMO():
    ''' Read full AMO series
    Usage: AMOfull = get_AMOfull(local=None)

    Parameters
    ----------
    local : str | None
        option to use local stored file

    Returns
    -------
    AMOseries : pd Series
        AMO monthly time series
    '''

    # set AMO file
    fnmAMO = 'https://www.esrl.noaa.gov/psd/data/correlation/amon.us.data'

    # read into pandas series
    vAMO = pd.read_csv(fnmAMO,sep='\s+',skiprows=1,skipfooter=3,header=None,engine='python')             .iloc[:,-12:].stack(dropna=True).values
    AMOseries = pd.Series(vAMO,index=pd.date_range(start='1948-01-01', periods=len(vAMO),freq='MS'))
    AMOseries.name = 'AMO'

    # replace -99 with NaN
    AMOseries.replace({-99.990:np.NaN},inplace=True)

    AMOseries = AMOseries.dropna()

    return AMOseries

# def plotONI(ONIts):
#     import matplotlib.pyplot as plt
#     import matplotlib.cm as pltcm
#     import seaborn as sns
#     fig,ax = plt.subplots(figsize=(18,6))
#     ONIts.plot(color='0.5',lw=0.5,ax=ax)
#     ONIts[ONIts>0].plot(lw=0,ax=ax)
#     ONIts[ONIts<0].plot(lw=0,ax=ax)
#
#     ONIts_gt0 = ONIts.copy()
#     ONIts_gt0[ONIts_gt0<0] = 0
#     ONIts_lt0 = ONIts.copy()
#     ONIts_lt0[ONIts_gt0>0] = 0
#     ax.fill_between(ONIts_gt0.index,ONIts_gt0.values,np.zeros(ONIts_gt0.size),color='r',alpha=0.7)
#     ax.fill_between(ONIts_lt0.index,ONIts_lt0.values,np.zeros(ONIts_lt0.size),color='b',alpha=0.7)
#
#     ax.set_xlim(ONIts.index[0],ONIts.index[-1])
#     ax.set_title('Ocean Nino Index')
#     _=ax.text(ONIts.index[10],2.4,'Last observation: '+str(ONIts.index[-1].year)+'/'+str(ONIts.index[-1].month).zfill(2))
#     return fig

def plotONI_alt(ONIts):
    import altair as alt
    dfONI = ONIts.to_frame(name='ONI')
    dfONI['date'] = dfONI.index.to_timestamp()
    c = alt.Chart(dfONI).mark_line().encode(
        x='date:T',
        y='ONI:Q',
        tooltip=['date','ONI']
    )
    return c

def plotAMO_alt(AMOts):
    import altair as alt
    dfAMO = AMOts.to_frame(name='AMO')
    dfAMO['date'] = dfAMO.index
    c = alt.Chart(dfAMO).mark_line().encode(
        x='date:T',
        y='AMO:Q',
        tooltip=['date','AMO']
    )
    return c

sOCI = st.sidebar.selectbox('Select OCI', ['ONI','AMO'])

if sOCI == 'ONI':
    # add a title
    st.title('Ocean Nino Index')
    st.write('[Data source](https://origin.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_v5.php)')

    # get ONIts data
    ONIts = getONI()

    # # plot using matplotlib
    # st.pyplot(plotONI(ONIts))

    # plot using altair
    st.header('Full')
    st.altair_chart(plotONI_alt(ONIts),use_container_width=True)

    # since 2000
    ONIts_2000 = ONIts.loc['2000-1-1':]
    st.header('Since 2000')
    st.altair_chart(plotONI_alt(ONIts_2000),use_container_width=True)

elif sOCI == 'AMO':
    # add a title
    st.title('Atlantic Multi-decadal Oscillation Index')
    st.write('[Data source](https://www.esrl.noaa.gov/psd/data/correlation/amon.us.data)')

    # get AMOts data
    AMOts = getAMO()

    # plot using altair
    st.header('Full')
    st.altair_chart(plotAMO_alt(AMOts),use_container_width=True)

    # since 2000
    AMOts_2000 = AMOts.loc['2000-1-1':]
    st.header('Since 2000')
    st.altair_chart(plotAMO_alt(AMOts_2000),use_container_width=True)
