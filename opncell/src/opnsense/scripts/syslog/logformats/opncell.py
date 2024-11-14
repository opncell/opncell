"""
    Copyright (c) 2024 Digital Solutions
    All rights reserved.
    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:
    1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.
    2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.
    THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES,
    INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
    AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
    AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
    OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
    SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
    INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
    CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
    ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
    POSSIBILITY OF SUCH DAMAGE.
"""
import datetime

from . import NewBaseLogFormat


# MME
class OpncoreMMELogFormat(NewBaseLogFormat):
    def __init__(self, filename):
        super().__init__(filename)
        self._priority = 1
        self._parts = list()

    def match(self, line):
        return self._filename.find('opncell/mme.log') > -1

    def set_line(self, line):
        super().set_line(line)
        self._parts = self._line.split(maxsplit=4)

    @property
    def timestamp(self):
        # opncore format return actual log data
        try:
            part_two = self._parts[1].strip(":")
            current_date = datetime.datetime.now()
            current_year = current_date.year
            log_date_str = f"{self._parts[0]}/{current_year}"
            ts = datetime.datetime.strptime(f"{log_date_str} {part_two}", "%m/%d/%Y %H:%M:%S.%f")
            return ts.isoformat()
        except:
            pass
    @property
    def severity(self):
        # Grab the log level Put in a try block because each service on startup has
        # "Open5GS daemon v2.6.6-26-ge12b1be" which breaks.

        options = {"INFO": 6, "ERROR": 3, "FATAL": 2, "WARNING":4 }
        try:
            severity = self._parts[3].strip(":")
            if severity in options:
                return options[severity]
            return None
        except:
            return options["INFO"]

    @property
    def process_name(self):
        # Grab the type of log message
        try:
            if self._parts[2].startswith("v") and not self._parts[2].startswith("["):
                return "[mme]"
            else:
                return self._parts[2].strip()
        except:
            pass

    @property
    def line(self):
        try:
            # Only grab the leftover message
            return self._parts[4].strip()
        except:
            if len(self._parts) > 1:
                return f"{self._parts[0]} {self._parts[1]} {self._parts[2] }"
            else:
                return f"{self._parts[0]}"

# UPF
class OpncoreUPFLogFormat(NewBaseLogFormat):
    def __init__(self, filename):
        super().__init__(filename)
        self._priority = 1
        self._parts = list()

    def match(self, line):
        return self._filename.find('opncell/upf.log') > -1

    def set_line(self, line):
        super().set_line(line)
        self._parts = self._line.split(maxsplit=4)

    @property
    def timestamp(self):
        # opncore format return actual log data
        try:
            part_two = self._parts[1].strip(":")
            current_date = datetime.datetime.now()
            current_year = current_date.year
            log_date_str = f"{self._parts[0]}/{current_year}"
            ts = datetime.datetime.strptime(f"{log_date_str} {part_two}", "%m/%d/%Y %H:%M:%S.%f")
            return ts.isoformat()
        except:
            pass

    @property
    def severity(self):
        # Grab the log level Put in a try block because each service on startup has
        # "Open5GS daemon v2.6.6-26-ge12b1be" which breaks.

        options = {"INFO": 6, "ERROR": 3, "FATAL": 2, "WARNING":4 }
        try:
            severity = self._parts[3].strip(":")
            if severity in options:
                return options[severity]
            return None
        except:
            return options["INFO"]

    @property
    def process_name(self):
        # Grab the type of log message
        try:
            if self._parts[2].startswith("v") and not self._parts[2].startswith("["):
                return "[upf]"
            else:
                return self._parts[2].strip()
        except:
            pass
    @property
    def line(self):
        try:
            # Only grab the left over message
            return self._parts[4].strip()
        except:
            if len(self._parts) > 1:
                return f"{self._parts[0]} {self._parts[1]} {self._parts[2] }"
            else:
                return f"{self._parts[0]}"



# UDM
class OpncoreUDMLogFormat(NewBaseLogFormat):
    def __init__(self, filename):
        super().__init__(filename)
        self._priority = 1
        self._parts = list()

    def match(self, line):
        return self._filename.find('opncell/udm.log') > -1

    def set_line(self, line):
        super().set_line(line)
        self._parts = self._line.split(maxsplit=4)

    @property
    def timestamp(self):
        # opncore format return actual log data
        try:
            part_two = self._parts[1].strip(":")
            current_date = datetime.datetime.now()
            current_year = current_date.year
            log_date_str = f"{self._parts[0]}/{current_year}"
            ts = datetime.datetime.strptime(f"{log_date_str} {part_two}", "%m/%d/%Y %H:%M:%S.%f")
            return ts.isoformat()
        except:
            pass

    @property
    def severity(self):
        # Grab the log level Put in a try block because each service on startup has
        # "Open5GS daemon v2.6.6-26-ge12b1be" which breaks.

        options = {"INFO": 6, "ERROR": 3, "FATAL": 2, "WARNING":4 }
        try:
            severity = self._parts[3].strip(":")
            if severity in options:
                return options[severity]
            return None
        except:
            return options["INFO"]

    @property
    def process_name(self):
        # Grab the type of log message
        try:
            if self._parts[2].startswith("v") and not self._parts[2].startswith("["):
                return "[udm]"
            else:
                return self._parts[2].strip()
        except:
            pass

    @property
    def line(self):
        try:
            # Only grab the left over message
            return self._parts[4].strip()
        except:
            if len(self._parts) > 1:
                return f"{self._parts[0]} {self._parts[1]} {self._parts[2] }"
            else:
                return f"{self._parts[0]}"


# SGWC
class OpncoreSGWCLogFormat(NewBaseLogFormat):
    def __init__(self, filename):
        super().__init__(filename)
        self._priority = 1
        self._parts = list()

    def match(self, line):
        return self._filename.find('opncell/sgwc.log') > -1

    def set_line(self, line):
        super().set_line(line)
        self._parts = self._line.split(maxsplit=4)

    @property
    def timestamp(self):
        # opncore format return actual log data
        try:
            part_two = self._parts[1].strip(":")
            current_date = datetime.datetime.now()
            current_year = current_date.year
            log_date_str = f"{self._parts[0]}/{current_year}"
            ts = datetime.datetime.strptime(f"{log_date_str} {part_two}", "%m/%d/%Y %H:%M:%S.%f")
            return ts.isoformat()
        except:
            pass

    @property
    def severity(self):
        # Grab the log level Put in a try block because each service on startup has
        # "Open5GS daemon v2.6.6-26-ge12b1be" which breaks.

        options = {"INFO": 6, "ERROR": 3, "FATAL": 2, "WARNING":4 }
        try:
            severity = self._parts[3].strip(":")
            if severity in options:
                return options[severity]
            return None
        except:
            return options["INFO"]

    @property
    def process_name(self):
        # Grab the type of log message
        try:
            if self._parts[2].startswith("v") and not self._parts[2].startswith("["):
                return "[sgwc]"
            else:
                return self._parts[2].strip()
        except:
            pass

    @property
    def line(self):
        try:
            # Only grab the left over message
            return self._parts[4].strip()
        except:
            if len(self._parts) > 1:
                return f"{self._parts[0]} {self._parts[1]} {self._parts[2] }"
            else:
                return f"{self._parts[0]}"

#SGWU
class OpncoreSGWULogFormat(NewBaseLogFormat):
    def __init__(self, filename):
        super().__init__(filename)
        self._priority = 1
        self._parts = list()

    def match(self, line):
        return self._filename.find('opncell/sgwu.log') > -1

    def set_line(self, line):
        super().set_line(line)
        self._parts = self._line.split(maxsplit=4)

    @property
    def timestamp(self):
        # opncore format return actual log data
        try:
            part_two = self._parts[1].strip(":")
            current_date = datetime.datetime.now()
            current_year = current_date.year
            log_date_str = f"{self._parts[0]}/{current_year}"
            ts = datetime.datetime.strptime(f"{log_date_str} {part_two}", "%m/%d/%Y %H:%M:%S.%f")
            return ts.isoformat()
        except:
            pass

    @property
    def severity(self):
        # Grab the log level Put in a try block because each service on startup has
        # "Open5GS daemon v2.6.6-26-ge12b1be" which breaks.

        options = {"INFO": 6, "ERROR": 3, "FATAL": 2, "WARNING":4 }
        try:
            severity = self._parts[3].strip(":")
            if severity in options:
                return options[severity]
            return None
        except:
            return options["INFO"]

    @property
    def process_name(self):
        # Grab the type of log message
        try:
            if self._parts[2].startswith("v") and not self._parts[2].startswith("["):
                return "[sgwu]"
            else:
                return self._parts[2].strip()
        except:
            pass

    @property
    def line(self):
        try:
            # Only grab the left over message
            return self._parts[4].strip()
        except:
            if len(self._parts) > 1:
                return f"{self._parts[0]} {self._parts[1]} {self._parts[2] }"
            else:
                return f"{self._parts[0]}"

#PCRF
class OpncorePCRFLogFormat(NewBaseLogFormat):
    def __init__(self, filename):
        super().__init__(filename)
        self._priority = 1
        self._parts = list()

    def match(self, line):
        return self._filename.find('opncell/pcrf.log') > -1

    def set_line(self, line):
        super().set_line(line)
        self._parts = self._line.split(maxsplit=4)

    @property
    def timestamp(self):
        # opncore format return actual log data
        try:
            part_two = self._parts[1].strip(":")
            current_date = datetime.datetime.now()
            current_year = current_date.year
            log_date_str = f"{self._parts[0]}/{current_year}"
            ts = datetime.datetime.strptime(f"{log_date_str} {part_two}", "%m/%d/%Y %H:%M:%S.%f")
            return ts.isoformat()
        except:
            pass

    @property
    def severity(self):
        # Grab the log level Put in a try block because each service on startup has
        # "Open5GS daemon v2.6.6-26-ge12b1be" which breaks.

        options = {"INFO": 6, "ERROR": 3, "FATAL": 2, "WARNING":4 }
        try:
            severity = self._parts[3].strip(":")
            if severity in options:
                return options[severity]
            return None
        except:
            return options["INFO"]

    @property
    def process_name(self):
        # Grab the type of log message
        try:
            if self._parts[2].startswith("v") and not self._parts[2].startswith("["):
                return "[pcrf]"
            else:
                return self._parts[2].strip()
        except:
            pass

    @property
    def line(self):
        try:
            # Only grab the left over message
            return self._parts[4].strip()
        except:
            if len(self._parts) > 1:
                return f"{self._parts[0]} {self._parts[1]} {self._parts[2] }"
            else:
                return f"{self._parts[0]}"

#SMF
class OpncoreSMFLogFormat(NewBaseLogFormat):
    def __init__(self, filename):
        super().__init__(filename)
        self._priority = 1
        self._parts = list()

    def match(self, line):
        return self._filename.find('opncell/smf.log') > -1

    def set_line(self, line):
        super().set_line(line)
        self._parts = self._line.split(maxsplit=4)

    @property
    def timestamp(self):
        # opncore format return actual log data
        try:
            part_two = self._parts[1].strip(":")
            current_date = datetime.datetime.now()
            current_year = current_date.year
            log_date_str = f"{self._parts[0]}/{current_year}"
            ts = datetime.datetime.strptime(f"{log_date_str} {part_two}", "%m/%d/%Y %H:%M:%S.%f")
            return ts.isoformat()
        except:
            pass

    @property
    def severity(self):
        # Grab the log level Put in a try block because each service on startup has
        # "Open5GS daemon v2.6.6-26-ge12b1be" which breaks.

        options = {"INFO": 6, "ERROR": 3, "FATAL": 2, "WARNING":4 }
        try:
            severity = self._parts[3].strip(":")
            if severity in options:
                return options[severity]
            return None
        except:
            return options["INFO"]

    @property
    def process_name(self):
        # Grab the type of log message
        try:
            if self._parts[2].startswith("v") and not self._parts[2].startswith("["):
                return "[smf]"
            else:
                return self._parts[2].strip()
        except:
            pass

    @property
    def line(self):
        try:
            # Only grab the left over message
            return self._parts[4].strip()
        except:
            if len(self._parts) > 1:
                return f"{self._parts[0]} {self._parts[1]} {self._parts[2] }"
            else:
                return f"{self._parts[0]}"

#NRF
class OpncoreNRFLogFormat(NewBaseLogFormat):
    def __init__(self, filename):
        super().__init__(filename)
        self._priority = 1
        self._parts = list()

    def match(self, line):
        return self._filename.find('opncell/nrf.log') > -1

    def set_line(self, line):
        super().set_line(line)
        self._parts = self._line.split(maxsplit=4)

    @property
    def timestamp(self):
        # opncore format return actual log data
        try:
            part_two = self._parts[1].strip(":")
            current_date = datetime.datetime.now()
            current_year = current_date.year
            log_date_str = f"{self._parts[0]}/{current_year}"
            ts = datetime.datetime.strptime(f"{log_date_str} {part_two}", "%m/%d/%Y %H:%M:%S.%f")
            return ts.isoformat()
        except:
            pass

    @property
    def severity(self):
        # Grab the log level Put in a try block because each service on startup has
        # "Open5GS daemon v2.6.6-26-ge12b1be" which breaks.

        options = {"INFO": 6, "ERROR": 3, "FATAL": 2, "WARNING":4 }
        try:
            severity = self._parts[3].strip(":")
            if severity in options:
                return options[severity]
            return None
        except:
            return options["INFO"]

    @property
    def process_name(self):
        # Grab the type of log message
        try:
            if self._parts[2].startswith("v") and not self._parts[2].startswith("["):
                return "[nrf]"
            else:
                return self._parts[2].strip()
        except:
            pass

    @property
    def line(self):
        try:
            # Only grab the left over message
            return self._parts[4].strip()
        except:
            if len(self._parts) > 1:
                return f"{self._parts[0]} {self._parts[1]} {self._parts[2] }"
            else:
                return f"{self._parts[0]}"

#SCP
class OpncoreSCPLogFormat(NewBaseLogFormat):
    def __init__(self, filename):
        super().__init__(filename)
        self._priority = 1
        self._parts = list()

    def match(self, line):
        return self._filename.find('opncell/scp.log') > -1

    def set_line(self, line):
        super().set_line(line)
        self._parts = self._line.split(maxsplit=4)

    @property
    def timestamp(self):
        # opncore format return actual log data
        try:
            part_two = self._parts[1].strip(":")
            current_date = datetime.datetime.now()
            current_year = current_date.year
            log_date_str = f"{self._parts[0]}/{current_year}"
            ts = datetime.datetime.strptime(f"{log_date_str} {part_two}", "%m/%d/%Y %H:%M:%S.%f")
            return ts.isoformat()
        except:
            pass

    @property
    def severity(self):
        # Grab the log level Put in a try block because each service on startup has
        # "Open5GS daemon v2.6.6-26-ge12b1be" which breaks.

        options = {"INFO": 6, "ERROR": 3, "FATAL": 2, "WARNING":4 }
        try:
            severity = self._parts[3].strip(":")
            if severity in options:
                return options[severity]
            return None
        except:
            return options["INFO"]

    @property
    def process_name(self):
        # Grab the type of log message
        try:
            if self._parts[2].startswith("v") and not self._parts[2].startswith("["):
                return "[scp]"
            else:
                return self._parts[2].strip()
        except:
            pass

    @property
    def line(self):
        try:
            # Only grab the left over message
            return self._parts[4].strip()
        except:
            if len(self._parts) > 1:
                return f"{self._parts[0]} {self._parts[1]} {self._parts[2] }"
            else:
                return f"{self._parts[0]}"

#AMF
class OpncoreAMFLogFormat(NewBaseLogFormat):
    def __init__(self, filename):
        super().__init__(filename)
        self._priority = 1
        self._parts = list()

    def match(self, line):
        return self._filename.find('opncell/amf.log') > -1

    def set_line(self, line):
        super().set_line(line)
        self._parts = self._line.split(maxsplit=4)

    @property
    def timestamp(self):
        # opncore format return actual log data
        try:
            part_two = self._parts[1].strip(":")
            current_date = datetime.datetime.now()
            current_year = current_date.year
            log_date_str = f"{self._parts[0]}/{current_year}"
            ts = datetime.datetime.strptime(f"{log_date_str} {part_two}", "%m/%d/%Y %H:%M:%S.%f")
            return ts.isoformat()
        except:
            pass

    @property
    def severity(self):
        # Grab the log level Put in a try block because each service on startup has
        # "Open5GS daemon v2.6.6-26-ge12b1be" which breaks.

        options = {"INFO": 6, "ERROR": 3, "FATAL": 2, "WARNING":4 }
        try:
            severity = self._parts[3].strip(":")
            if severity in options:
                return options[severity]
            return None
        except:
            return options["INFO"]

    @property
    def process_name(self):
        # Grab the type of log message
        try:
            if self._parts[2].startswith("v") and not self._parts[2].startswith("["):
                return "[amf]"
            else:
                return self._parts[2].strip()
        except:
            pass

    @property
    def line(self):
        try:
            # Only grab the left over message
            return self._parts[4].strip()
        except:
            if len(self._parts) > 1:
                return f"{self._parts[0]} {self._parts[1]} {self._parts[2] }"
            else:
                return f"{self._parts[0]}"

#AUSF
class OpncoreAUSFLogFormat(NewBaseLogFormat):
    def __init__(self, filename):
        super().__init__(filename)
        self._priority = 1
        self._parts = list()

    def match(self, line):
        return self._filename.find('opncell/ausf.log') > -1

    def set_line(self, line):
        super().set_line(line)
        self._parts = self._line.split(maxsplit=4)

    @property
    def timestamp(self):
        # opncore format return actual log data
        try:
            part_two = self._parts[1].strip(":")
            current_date = datetime.datetime.now()
            current_year = current_date.year
            log_date_str = f"{self._parts[0]}/{current_year}"
            ts = datetime.datetime.strptime(f"{log_date_str} {part_two}", "%m/%d/%Y %H:%M:%S.%f")
            return ts.isoformat()
        except:
            pass

    @property
    def severity(self):
        # Grab the log level Put in a try block because each service on startup has
        # "Open5GS daemon v2.6.6-26-ge12b1be" which breaks.

        options = {"INFO": 6, "ERROR": 3, "FATAL": 2, "WARNING":4 }
        try:
            severity = self._parts[3].strip(":")
            if severity in options:
                return options[severity]
            return None
        except:
            return options["INFO"]

    @property
    def process_name(self):
        # Grab the type of log message
        try:
            if self._parts[2].startswith("v") and not self._parts[2].startswith("["):
                return "[ausf]"
            else:
                return self._parts[2].strip()
        except:
            pass

    @property
    def line(self):
        try:
            # Only grab the left over message
            return self._parts[4].strip()
        except:
            if len(self._parts) > 1:
                return f"{self._parts[0]} {self._parts[1]} {self._parts[2] }"
            else:
                return f"{self._parts[0]}"

#UDR
class OpncoreUDRLogFormat(NewBaseLogFormat):
    def __init__(self, filename):
        super().__init__(filename)
        self._priority = 1
        self._parts = list()

    def match(self, line):
        return self._filename.find('opncell/udr.log') > -1

    def set_line(self, line):
        super().set_line(line)
        self._parts = self._line.split(maxsplit=4)

    @property
    def timestamp(self):
        # opncore format return actual log data
        try:
            part_two = self._parts[1].strip(":")
            current_date = datetime.datetime.now()
            current_year = current_date.year
            log_date_str = f"{self._parts[0]}/{current_year}"
            ts = datetime.datetime.strptime(f"{log_date_str} {part_two}", "%m/%d/%Y %H:%M:%S.%f")
            return ts.isoformat()
        except:
            pass

    @property
    def severity(self):
        # Grab the log level Put in a try block because each service on startup has
        # "Open5GS daemon v2.6.6-26-ge12b1be" which breaks.

        options = {"INFO": 6, "ERROR": 3, "FATAL": 2, "WARNING":4 }
        try:
            severity = self._parts[3].strip(":")
            if severity in options:
                return options[severity]
            return None
        except:
            return options["INFO"]

    @property
    def process_name(self):
        # Grab the type of log message
        try:
            if self._parts[2].startswith("v") and not self._parts[2].startswith("["):
                return "[udr]"
            else:
                return self._parts[2].strip()
        except:
            pass

    @property
    def line(self):
        try:
            # Only grab the left over message
            return self._parts[4].strip()
        except:
            if len(self._parts) > 1:
                return f"{self._parts[0]} {self._parts[1]} {self._parts[2] }"
            else:
                return f"{self._parts[0]}"

#PCF
class OpncorePCFLogFormat(NewBaseLogFormat):
    def __init__(self, filename):
        super().__init__(filename)
        self._priority = 1
        self._parts = list()

    def match(self, line):
        return self._filename.find('opncell/pcf.log') > -1

    def set_line(self, line):
        super().set_line(line)
        self._parts = self._line.split(maxsplit=4)

    @property
    def timestamp(self):
        # opncore format return actual log data
        try:
            part_two = self._parts[1].strip(":")
            current_date = datetime.datetime.now()
            current_year = current_date.year
            log_date_str = f"{self._parts[0]}/{current_year}"
            ts = datetime.datetime.strptime(f"{log_date_str} {part_two}", "%m/%d/%Y %H:%M:%S.%f")
            return ts.isoformat()
        except:
            pass

    @property
    def severity(self):
        # Grab the log level Put in a try block because each service on startup has
        # "Open5GS daemon v2.6.6-26-ge12b1be" which breaks.

        options = {"INFO": 6, "ERROR": 3, "FATAL": 2, "WARNING":4 }
        try:
            severity = self._parts[3].strip(":")
            if severity in options:
                return options[severity]
            return None
        except:
            return options["INFO"]

    @property
    def process_name(self):
        # Grab the type of log message
        try:
            if self._parts[2].startswith("v") and not self._parts[2].startswith("["):
                return "[pcf]"
            else:
                return self._parts[2].strip()
        except:
            pass

    @property
    def line(self):
        try:
            # Only grab the left over message
            return self._parts[4].strip()
        except:
            if len(self._parts) > 1:
                return f"{self._parts[0]} {self._parts[1]} {self._parts[2] }"
            else:
                return f"{self._parts[0]}"

#BSF
class OpncoreBSFLogFormat(NewBaseLogFormat):
    def __init__(self, filename):
        super().__init__(filename)
        self._priority = 1
        self._parts = list()

    def match(self, line):
        return self._filename.find('opncell/bsf.log') > -1

    def set_line(self, line):
        super().set_line(line)
        self._parts = self._line.split(maxsplit=4)

    @property
    def timestamp(self):
        # opncore format return actual log data
        try:
            part_two = self._parts[1].strip(":")
            current_date = datetime.datetime.now()
            current_year = current_date.year
            log_date_str = f"{self._parts[0]}/{current_year}"
            ts = datetime.datetime.strptime(f"{log_date_str} {part_two}", "%m/%d/%Y %H:%M:%S.%f")
            return ts.isoformat()
        except:
            pass

    @property
    def severity(self):
        # Grab the log level Put in a try block because each service on startup has
        # "Open5GS daemon v2.6.6-26-ge12b1be" which breaks.

        options = {"INFO": 6, "ERROR": 3, "FATAL": 2, "WARNING":4 }
        try:
            severity = self._parts[3].strip(":")
            if severity in options:
                return options[severity]
            return None
        except:
            return options["INFO"]

    @property
    def process_name(self):
        # Grab the type of log message
        try:
            if self._parts[2].startswith("v") and not self._parts[2].startswith("["):
                return "[bsf]"
            else:
                return self._parts[2].strip()
        except:
            pass

    @property
    def line(self):
        try:
            # Only grab the left over message
            return self._parts[4].strip()
        except:
            if len(self._parts) > 1:
                return f"{self._parts[0]} {self._parts[1]} {self._parts[2] }"
            else:
                return f"{self._parts[0]}"

#HSS
class OpncoreHSSLogFormat(NewBaseLogFormat):
    def __init__(self, filename):
        super().__init__(filename)
        self._priority = 1
        self._parts = list()

    def match(self, line):
        return self._filename.find('opncell/hss.log') > -1

    def set_line(self, line):
        super().set_line(line)
        self._parts = self._line.split(maxsplit=4)

    @property
    def timestamp(self):
        # opncore format return actual log data
        try:
            part_two = self._parts[1].strip(":")
            current_date = datetime.datetime.now()
            current_year = current_date.year
            log_date_str = f"{self._parts[0]}/{current_year}"
            ts = datetime.datetime.strptime(f"{log_date_str} {part_two}", "%m/%d/%Y %H:%M:%S.%f")
            return ts.isoformat()
        except:
            pass

    @property
    def severity(self):
        # Grab the log level Put in a try block because each service on startup has
        # "Open5GS daemon v2.6.6-26-ge12b1be" which breaks.

        options = {"INFO": 6, "ERROR": 3, "FATAL": 2, "WARNING":4 }
        try:
            severity = self._parts[3].strip(":")
            if severity in options:
                return options[severity]
            return None
        except:
            return options["INFO"]

    @property
    def process_name(self):
        # Grab the type of log message
        try:
            if self._parts[2].startswith("v") and not self._parts[2].startswith("["):
                return "[hss]"
            else:
                return self._parts[2].strip()
        except:
            pass


    @property
    def line(self):
        try:
            # Only grab the left over message
            return self._parts[4].strip()
        except:
            if len(self._parts) > 1:
                return f"{self._parts[0]} {self._parts[1]} {self._parts[2] }"
            else:
                return f"{self._parts[0]}"