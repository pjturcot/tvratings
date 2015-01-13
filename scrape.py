# Code for scraping
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import parsedatetime as pdt
import urllib2
import collections
import wikipedia
import datetime

EpisodeStats = collections.namedtuple('EpisodeStats', ['number','date','viewers'])

class EpisodeListScraper:
    def __init__( self ):
        self.TABLE_SERIES_NUM = "series"
        self.TABLE_VIEWERS = "viewers"
        self.TABLE_DATE= "air date"
        self.dt_parse = pdt.Calendar()
    
    '''Get the stats for a tvshow by name.''' 
    def get_show_stats(self, show_name ):
        result = wikipedia.search( 'list of %s episodes' % show_name.lower())[0]
        url = wikipedia.page( result ).url
        return self.scrape_url( url )

    def plot_by_number( self, show_name, **kwargs ):
        stats = self.get_show_stats( show_name )
        plt.plot( [ x.number for x in stats ], [x.viewers for x in stats ], **kwargs )

    def plot_by_date( self, show_name, **kwargs ):
        stats = self.get_show_stats( show_name )
        plt.plot( [ datetime.datetime(*(x.date[:3])) for x in stats ], [x.viewers for x in stats ], **kwargs )

        
    '''Convert table date string into a usable date.'''
    def to_date(self, datestr ):
        return self.dt_parse.parse(datestr.split('(')[0])

    '''Scrape the URL and return the stats.'''
    def scrape_url( self, url ):
        soup = BeautifulSoup( urllib2.urlopen( url ))
        stats = []
        for t in soup.find_all('table'):
            if self.check_table( t ):
                stats += self.parse_table( t )
        return stats
    
    '''Convert a single table into episode stats.'''
    def parse_table( self, table ):
        header, data = self.scrape_table( table )
        number_index = min( [ i for i,h in enumerate(header) if self.TABLE_SERIES_NUM in h ])
        viewers_index = min( [ i for i,h in enumerate(header) if self.TABLE_VIEWERS in h ])
        date_index = min( [ i for i,h in enumerate(header) if self.TABLE_DATE in h ])
        stats = []

        for d in data:
            try:
                number = int( d[number_index].split('/')[0] )
                viewers = float( d[viewers_index].split('[')[0] )
                date = self.to_date( d[date_index])[0]
                stats.append( EpisodeStats( number=number, viewers=viewers, date=date ))
            except ValueError as e:
                print "Failed to parse : ", d 
        return stats

    '''Returns true if table contains episode information.'''
    def check_table(self, table):
        header = table.find('tr')
        header_str = str(header)
        return self.TABLE_VIEWERS in header_str and self.TABLE_DATE in header_str and self.TABLE_SERIES_NUM in header_str

    '''Parse out the header and valid data rows.'''
    def scrape_table( self, table ):
        clean = lambda x: ''.join( x.strings ).replace(u'\xa0', ' ').replace('\n', ' ')
        rows = table.find_all('tr')
        header = [ clean(x) for x in rows[0].find_all( ['td','th']) ]
        data = []
        for row in rows[1:]: # Data rows only
            cells = row.find_all( ['td','th'] )
            if len(cells) != len(header):
                continue
            data.append( [ clean(x) for x in cells ] )
        return header, data
