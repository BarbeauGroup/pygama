from abc import ABC
from raw_buffer import RawBufferLibrary

class DataStreamer(ABC):
    """ Base clase for data streams 

    Provides a uniform interface for streaming, e.g.

    > header = ds.open_stream(stream_name)
    > for chunk in ds: do_something(chunk)

    Also provides default management of the RawBufferLibrary used for data reading:
    - allocation (if needed)
    - configuration (to match the stream)
    - fill level checking

    Derived classes must define the functions get_decoder_list(), open_stream(),
    and read_packet(); see below.
    """

    def __init__(self):
        self.rb_lib = None
        self.chunk_mode = None
        self.n_bytes_read = 0
        self.any_full = False


    def open_stream(self, stream_name, rb_lib=None, buffer_size=8192,
                    chunk_mode='any_full', out_stream='', verbosity=0):
        """ Open and initialize a data stream

        Open the stream, read in the header, set up the buffers

        Call super().initialize([args]) from derived class after loading header
        info to run this default version that sets up buffers in rb_lib using
        the stream's decoders

        Note: this default version has no actual return value! You must overload
        this function, set self.n_bytes_read to the header packet size, and
        return the header data

        Parameters
        ----------
        stream_name : str
            typically a filename or e.g. a port for streaming
        rb_lib : RawBufferLibrary
            A library of buffers for readout from the data stream. rb_lib will
            have its lgdo's initialized during this function
        buffer_size : int
            length of buffers to be read out in read_chunk (for buffers with
            variable length)
        chunk_mode : 'any_full', 'only_full', or 'single_packet'
            sets the mode use for read_chunk
        out_stream : str
            optional name of output stream for default rb_lib generation
        verbosity : int
            verbosity level for the initialize function

        Returns
        -------
        header_data: list(RawBuffer), int
            header_data is a list of RawBuffer's containing any file header
                data, ready for writing to file or further processing. It's not
                a RawBufferList since the buffers may have a different format
        """
        # call super().initialize([args]) to run this default code
        # after loading header info, then follow it with the return call.

        # store chunk mode
        self.chunk_mode = chunk_mode

        # prepare rb_lib -- its lgdo's should still be uninitialized
        if rb_lib is None: rb_lib = self.build_default_rb_lib(out_stream=out_stream)
        self.rb_lib = rb_lib

        # now initialize lgdo's for raw buffers
        decoders = self.get_decoder_list()
        dec_names = []
        for decoder in decoders:
            dec_name = type(decoder).__name__

            # set up wildcard buffers
            if dec_name not in rb_lib 
                if '*' not in rb_lib: continue # user didn't want this decoder
                dec_key = dec_name
                if dec_key.endswith('Decoder'): dec_key.removesuffix('Decoder')
                out_name = rb_lib['*'][0].out_name.format('name'=dec_key)
                out_stream = rb_lib['*'][0].out_stream.format('name'=dec_key)
                rb = RawBuffer(out_stream=out_stream, out_name=decoder)
                rb_lib[dec_name] = RawBufferList()
                rb_lib[dec_name].append(rb)

            # dec_name is in rb_lib: store the name, and initialize its buffer lgdos
            dec_names.append(dec_name)
            rb_lib[dec_name].make_lgdos(decoder, size=buffer_size)

        # make sure there were no entries in rb_lib that weren't among the
        # decoders. If so, just emit a warning and continue.
        for dec_name in rb_lib.keys():
            if dec_name not in dec_names:
                print(f"Warning: no decoder named {dec_name} requested by rb_lib")



    def read_packet(self, verbosity=0):
        """
        Reads a single packet's worth of data in to the rb_lib

        Needs to be overloaded. Gets called by read_chunk()

        Needs to update self.any_full if any buffers would possibly over-fill on
        the next read

        Needs to update self.n_bytes_read too

        Returns
        -------
        still_has_data : bool
            Returns true while there is still data to read
        """
        return true


    def read_chunk(self, chunk_mode_override=None, rp_max=1000000, verbosity=0):
        """
        Reads a chunk of data into raw buffers

        Reads packets until at least one buffer is too full to perform another
        read.

        Note: user is responsible for resetting / clearing the raw buffers prior
        to calling read_chunk again.

        Default version just calls read_packet() over and over. Overload as
        necessary.

        Parameters
        ----------
        chunk_mode_override: 'any_full', 'only_full', 'single_packet', or None
            None : do not override self.chunk_mode
            'any_full' : returns all raw buffers with data as soon as any one
                buffer gets full
            'only_full' : returns only those raw buffers that became full (or
                nearly full) during the read. This minimizes the number of write calls.
            'single_packet' : returns all raw buffers with data after a single
                read is performed. This is useful for streaming data out as soon
                as it is read in (e.g. for diagnostics or in-line analysis)
        rp_max : int
            maximum number of packets to read before returning anyway, even if
            one of the other conditions is not met
        verbosity : int
            verbosity level for the initialize function

        Returns
        -------
        chunk_list, n_bytes : list of RawBuffers, int
            chunk_list is the list of RawBuffers with data ready for writing to
                file or further processing. The list contains all buffers with
                data or just all full buffers depending on the flag full_only.
                Note chunk_list is not a RawBufferList since the RawBuffers
                inside may not all have the same structure
            n_bytes is the number of bytes read from the file during this
                iteration.
        """

        chunk_mode = self.chunk_mode if chunk_mode_override is None else chunk_mode_override 

        read_one_packet = (chunk_mode == 'single_packet')
        only_full = (chunk_mode == 'only_full')

        n_packets = 0
        while True:
            still_has_data = self.read_packet()
            if (not still_has_data) break
            n_packets += 1
            if read_one_packet or n_packets > rp_max: break
            if self.any_full break

        list_of_rbs = []
        for rb_list in self.rb_lib.items():
            for rb in rb_list:
                if not only_full and rb.loc > 0: list_of_rbs.append(rb)
                else:
                    if not hasattr(rb.lgod, __len__):
                        if rb.loc > 0: list_of_rbs.append(rb)
                    else:
                        if rb.loc == len(rb.lgdo): list_of_rbs.append(rb)

        return list_of_rbs

        


    def get_decoder_list(self):
        """Returns a list of decoder objects for this data stream.
        Needs to be overloaded. Gets called during open_stream().
        """
        return []


    def build_default_rb_lib(self, out_stream=''):
        """ Build the most basic RawBufferLibrary that will work for this stream.

        A RawBufferList containing a single RawBuffer is built for each decoder
        name returned by get_decoder_list. Each buffer's out_name is set to the
        decoder name. The lgdo's do not get initialized.
        """
        rb_lib = RawBufferLibrary()
        decoders = self.get_decoder_list()
        if len(decoders) == 0:
            print(f'No decoders returned by get_decoder_list() for {type(self).__name__}')
            return rb_lib
        for decoder in decoders:
            dec_name = type(decoder).__name__
            rb = RawBuffer(out_stream=out_stream, out_name=dec_name)
            rb_lib[dec_name] = RawBufferList()
            rb_lib[dec_name].append(rb)
