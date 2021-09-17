import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

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

    dfONI = ONIts.to_frame(name='ONI')
    dfONI['date'] = dfONI.index.to_timestamp()

    return dfONI

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

    dfAMO = AMOseries.to_frame(name='AMO')
    dfAMO['date'] = dfAMO.index

    return dfAMO


sOCI = st.sidebar.selectbox('Select OCI', ['ONI','AMO'])

if sOCI == 'ONI':
    # add a title
    st.title('Ocean Nino Index')

    # get ONIts data
    dfONI = getONI()
    m_upd = dfONI['date'].iloc[-1].strftime('%b %Y')
    st.write(f'Updated as of {m_upd}, [Data source](https://origin.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_v5.php)')
    # # plot using matplotlib
    # st.pyplot(plotONI(ONIts))

    # plot using altair
    st.header('Full')
    c = alt.Chart(dfONI).mark_line().encode(
        x='date:T',
        y='ONI:Q',
        tooltip=['date','ONI']
    )
    st.altair_chart(c,use_container_width=True)

    # since 2000
    dfONI_2000 = dfONI.loc['2000-1-1':]
    st.header('Since 2000')
    c = alt.Chart(dfONI_2000).mark_line().encode(
        x='date:T',
        y='ONI:Q',
        tooltip=['date','ONI']
    )
    st.altair_chart(c,use_container_width=True)

elif sOCI == 'AMO':
    # add a title
    st.title('Atlantic Multi-decadal Oscillation Index')

    # get AMOts data
    dfAMO = getAMO()
    m_upd = dfAMO['date'].iloc[-1].strftime('%b %Y')
    st.write(f'Updated as of {m_upd}, [Data source](https://www.esrl.noaa.gov/psd/data/correlation/amon.us.data)')

    # plot using altair
    st.header('Full')
    c = alt.Chart(dfAMO).mark_line().encode(
        x='date:T',
        y='AMO:Q',
        tooltip=['date','AMO']
    )
    st.altair_chart(c,use_container_width=True)

    # since 2000
    dfAMO_2000 = dfAMO.loc['2000-1-1':]
    st.header('Since 2000')
    c = alt.Chart(dfAMO_2000).mark_line().encode(
        x='date:T',
        y='AMO:Q',
        tooltip=['date','AMO']
    )
    st.altair_chart(c,use_container_width=True)
