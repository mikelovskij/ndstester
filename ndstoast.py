import nds2
from log import Logger
from gwpy.time import tconvert
from numpy.random import randint

__author__ = 'mikelovskij'

# TODO: implement a timeout routine?

class NdsTester(object):
    def __init__(self, logger=Logger):
        self.logger = logger('NDS tester')
        self.gpsb = int(tconvert('now') - 1200)

    def connect_iterator(self, serv):
        for ifo, s in serv.iteritems:
            self.logger.info('Testing connection to server at {0} ({1})...'.format(ifo, s))
            try:
                conn = nds2.connection(s)
                self.logger.success('Connection establilished, printing details... \n {0}'.format(conn))
            except:
                self.logger.error("""Unable to open connection with server... \n {0},'
                                   the test will skip this server""".format(s))
                continue
            yield conn

    def connection_tester(self, ifo, s):
        self.logger.info('Testing connection to server at {0} ({1})...'.format(ifo, s))
        try:
            conn = nds2.connection(s)
            self.logger.success('Connection established, printing details... \n {0}'.format(conn))
            return conn
        except Exception as e:
            self.logger.error('Unable to open connection with server... \n {0}, {1}'.format(s, e))
            return e

    def available_channels_tester(self, conn):
        self.logger.info('Checking available online channels for connection {0}...'.format(conn))
        try:
            achannels = conn.find_channels('*', nds2.channel.CHANNEL_TYPE_ONLINE)
            self.logger.success('The available channels are {0}'.format(achannels))
            return achannels
        except Exception as e:
            self.logger.error('Unable to retrieve online channel list... \n {0}'.format(e))
            return e

    def iterator_tester(self, it):
        try:
            self.logger.info('Attempting to iterate on the generated iterator')
            data = next(it)
            self.logger.success('Iteration success: data = {0}'. format(data))
        except Exception as e:
            self.logger.error('Error {1} encountered while attempting to iterate on the iterator {0}'.format(it, e))

    def tester(self, testchannels=[], servers=None, gpsb=None, gpse=None, stride=5, nrand=10, avail_check=True):
        """
        This function executes the main testing routine
        (which is repeated for every server provided or from the default ones if no servers are provided) :
        *a nds connection is created,
        *(if 'avail_check' is True) the list of online available channels is requested from the server
        *(if 'avail_check' is True) a random sublist of 'nrand' channels from this list is selected
        * this list is then merged with eventual 'testchannels' manually provided
        *for every channel in this comprehensive list, the following tests are performed:
        ** an offline iterator asking data from 'gpsb' to 'gpse' is created (if no gps are provided,
            'gpsb' will be the gps 20 minutes before the class was instanced, and  'gpse' 10 minutes later)
        ** one iteration is made on such iterator
        ** an iterator asking online data is created
        ** one iteration is made on such iterator


        :param testchannels:
            list of names of the channels to test, without the ifo prefix e.g. ['OAF-CAL_DARM_DQ', ...]
            default = []
        :param servers:
            dictionary containing the address of the server to be tested as keys, and the name of the ifo of that server
             as values. e.g. {'nds.ligo-la.caltech.edu': 'L1', ...}
             default = {'nds.ligo-la.caltech.edu': 'L1', 'nds.ligo-wa.caltech.edu': 'H1'}
        :param gpsb:
            starting gps for the offline iterator test
            default = gps 20 minutes before the class was instanced
        :param gpse:
            ending gps for the offline iterator test
            default = gpsb + 600
        :param stride:
            length (in seconds) of the data requested for each iteration of the generated iterators
            default = 5
        :param nrand:
            If 'avail_check' is True, number of random channels to be tested,
            chosen from the available online channels for that server.
            default = 10
        :param avail_check:
            boolean, indicates whether or not the available online channels for a servers are requested. This process
            could require a lot of time.
            default = True
        """

        if servers is None:
            servers = {'nds.ligo-la.caltech.edu': 'L1', 'nds.ligo-wa.caltech.edu': 'H1'}
        if gpsb is None:
            gpsb = self.gpsb
        if gpse is None:
            gpse = gpsb + 600
        for interf, serv in servers.iteritems():
            # attempt to connect to the nds server
            connection = self.connection_tester(interf, serv)
            if isinstance(connection, Exception):
                self.logger.info('The test will skip this server')
                continue
            # retrieve the list of available online channels on this server
            if avail_check:
                avail_channels = self.available_channels_tester(connection)
                if isinstance(avail_channels, Exception):
                    self.logger.info('The test will skip this server')
                    continue
                # select some random channels between the available channels on which attempt the test
                rindexes = randint(len(avail_channels), size=nrand)
                random_channels = [avail_channels[i] for i in rindexes]
            else:
                random_channels = []
                avail_channels = []
            for c in set(testchannels + random_channels):
                # check that the channel is in the list of available channels
                if (c in avail_channels) or not avail_check:
                    c = interf + ':' + c
                    # try to create an offline iterator with this connection and channel
                    self.logger.info("""Creating an offline iterator for channel {0} on server
                     {1} using "conn.iterate({2}, {3}, {4}, [{0}])...""".format(c, serv, gpsb, gpse, stride))
                    try:
                        iterator = connection.iterate(gpsb, gpse, stride, [c])
                        self.logger.success('Offline iterator for channel {0} on server {1} created.'.format(c, serv))
                    except Exception as e:
                        self.logger.error("""Error {2} in creating the offline iterator for channel {0}
                         on server {1}, continuing the test.""".format(c, serv, e))
                    else:
                        # try to iterate on the offline iterator
                        self.iterator_tester(iterator)
                    self.logger.info('Proceeding with the test, resetting connection')
                    del connection
                    connection = self.connection_tester(interf, serv)
                    if isinstance(connection, Exception):
                        self.logger.error("""Error encountered in recreating the connection on server {0},
                         the test on this server will be interrupted""".format(serv))
                        break
                    self.logger.info("""Creating an online iterator for channel {0} on server
                     {1} using "conn.iterate({2}, [{0}])...""".format(c, serv, stride))
                    try:
                        iterator = connection.iterate(stride, [c])
                        self.logger.success('Online iterator for channel {0} on server {1} created.'.format(c, serv))
                    except Exception as e:
                        self.logger.error("""Error {2} in creating the online iterator for channel {0}
                         on server {1}, skipping channel.""".format(c, serv, e))
                    else:
                        # try to iterate on the online iterator
                        self.iterator_tester(iterator)
                    self.logger.info('Proceeding with the test, resetting connection')
                    del connection
                    connection = self.connection_tester(interf, serv)
                    if isinstance(connection, Exception):
                        self.logger.error("""Error encountered in recreating the connection on server {0},
                         the test on this server will be interrupted""".format(serv))
                        break
        self.logger.success('Test complete!')
