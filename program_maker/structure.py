from time import gmtime, strftime, strptime
from collections import OrderedDict
from csv import DictReader
from hashlib import sha1
from orderedset import OrderedSet
from unidecode import unidecode as remove_accents
from titlecase import titlecase

from unicode_tex import unicode_to_tex

# helper functions
def unicode_list(txt, separator=","):
    # helper
    lst = unicode(txt, 'utf-8').split(separator)
    return [x.strip() for x in lst]


def initials(name):
    # returns the initals of a name
    return ". ".join([x[0] for x in name.strip().split()]) + "."

def fix_uppercase(textstring, percent_uppercase_threshold=75):
    # converts string to titlecase (NY times style), if all
    #  (A) case are lower cases
    #  (B) x-% are in uppercase (see percent_uppercase_threshold)

    n = len(textstring)
    n_upper = sum([x.isupper() for x in textstring])
    if (n_upper==0) or (100*float(n_upper)/n)>percent_uppercase_threshold:
        return titlecase(textstring)
    else:
        return textstring

def secure_hash(filename):
    """returns sha1 secure hash from file or None, if not possile"""
    try:
        with open(filename) as f:
            return sha1(f.read()).hexdigest()
    except:
        return None

class Authors():

    def __init__(self, authors_csv_file):
        self.authors = []
        self.file = authors_csv_file
        self.file_hash = secure_hash(self.file)
        with open(authors_csv_file, 'rb') as csvfile:
            for row in DictReader(csvfile, delimiter=',', quotechar='"'):
                self.authors.append(row)
        self.names = OrderedSet([unicode(x['name'], 'utf-8') for x in self.authors] )

    def get_field(self, author_name, field):
        try:
            id = self.names.index(author_name)
        except:
            return None
        return self.authors[id][field]

    def get_organisations(self, author_name):
        a = self.get_field(author_name, "organisation")
        if a is None:
            return None
        else:
            return unicode_list(a, separator=";")


class Contribution():

    def __init__(self, authors, title, organizations, abstract, type, start, end, emails, fix_uppercase_title=True):
        # organisations for each author len(authors)==len(organizations)
        # multiple organisation of one authors are seperated by ";"
        # start ,end: time.struct_time

        self.authors = authors
        self.title = title
        self.abstract = abstract
        self.type = type
        self.start = start
        self.end = end
        self.emails = emails

        if fix_uppercase_title:
            self.title = fix_uppercase(self.title)

        # find all organizations
        self.unique_organisations = []
        self.organisations = []
        for orga in organizations:
            tmp = [x.strip() for x in orga.split(";")]
            self.organisations.append(tmp)
            self.unique_organisations.extend(tmp)
        self.unique_organisations = OrderedSet(self.unique_organisations)

        self.first_names = []
        self.last_names = []
        self.affiliation_ids = []
        for aut, orga in zip(self.authors, self.organisations):
            last, first = aut.title().split(",")
            self.last_names.append(last.strip())
            self.first_names.append(first.strip())

            idx = [self.unique_organisations.index(o)+1 for o in orga]
            self.affiliation_ids.append(idx)


    def formated_authors(self, fullnames=False, first_name_initials=False,
                affiliation_ids=False, orga_id_format=u"[{0}]",
                tex_code=False, write_index=False):
        # tex_code=True: convert all unicode strings to text code, except keep untouched "orga_id_format"
        # write_index: add index code (has only an effect if tex_code=True)

        if len(self.authors) == 1:
            if fullnames:
                rtn = self.first_names[0] + " " + self.last_names[0]
            else:
                rtn = self.last_names[0]
                if first_name_initials:
                    rtn += ", " + initials(self.first_names[0])
            if tex_code:
                rtn = unicode_to_tex(rtn)
                if write_index:
                    rtn += u"\\index{" + unicode_to_tex(remove_accents(self.last_names[0] + ", "
                                                                       + initials(self.first_names[0]))) + u"}"
            return rtn

        else:
            rtn = u""
            sep = u", "
            for cnt, last_name in enumerate(self.last_names):
                if cnt == len(self.last_names)-1:
                    sep = u" & "

                if fullnames:
                    name = sep + self.first_names[cnt] + " " + last_name
                else:
                    name = sep + last_name
                    if first_name_initials:
                        name += ", " + initials(self.first_names[cnt])
                if tex_code:
                    rtn += unicode_to_tex(name)
                    if write_index:
                        rtn += u"\\index{" + unicode_to_tex(remove_accents(last_name + ", "
                                                                           + initials(self.first_names[cnt]))) + u"}"
                else:
                    rtn += name
                if affiliation_ids and len(self.unique_organisations)>1:
                    rtn += orga_id_format.format(unicode(self.affiliation_ids[cnt])[1:-1])

            return rtn[2:]


    def formated_organisations(self, orga_id_format = u"[{0}] ", tex_code=False):
        # tex_code=True: convert all unicode strings to text code, except keep untouched "orga_id_format"

        if len(self.unique_organisations) == 1:
            if tex_code:
                return unicode_to_tex(self.unique_organisations[0])
            else:
                return self.unique_organisations[0]
        else:
            rtn = u""
            for cnt, orga in enumerate(self.unique_organisations):
                if tex_code:
                    orga = unicode_to_tex(orga)
                rtn += "; " + orga_id_format.format(cnt + 1) + orga
            return rtn[2:]

    @property
    def first_author_lastname(self):
        return self.last_names[0]

    @property
    def first_author_email(self):
        return self.emails[0]

    @property
    def start_str(self):
        return strftime("%H:%M", self.start)

    @property
    def start_str_long(self):
        return strftime("%d %b %Y %H:%M", self.start)

    @property
    def end_str(self):
        return strftime("%H:%M", self.end)


class Session():

    def __init__(self, entry_dict, max_contributions=80):
        # entry_dict: entry from csv file DictReader

        self.dict = entry_dict
        self.start = strptime(self.dict['session_start'], "%Y-%m-%d %H:%M")
        self.end = strptime(self.dict['session_end'], "%Y-%m-%d %H:%M")
        self.room =  self.dict['session_room']
        self.chair = unicode(entry_dict['chair1'], 'utf-8').strip()

        # symposia have the organizior in title [title (organizor)]
        self.title = unicode(entry_dict['session_title'].strip(), 'utf-8')
        self.symposium__organizer = None
        self.type = None
        if entry_dict['session_short'].startswith("Pos"):
            self.type = "poster"
        else:
            self.type = "oral"
            if self.title.endswith(")"): # symposium
                idx = self.title.rfind("(")
                self.symposium__organizer = self.title[idx+1:-1]
                self.title = self.title[:idx].strip()
                self.type = "symposium"

        self.contributions = []
        for x in xrange(1, max_contributions):
            title = unicode(entry_dict['p{}_title'.format(x)], 'utf-8')
            if len(title)!=0:
                authors = unicode_list(entry_dict['p{}_authors'.format(x)], separator="\n")
                emails = unicode_list(entry_dict['p{}_emails'.format(x)], separator="\n")
                organizations = unicode_list(entry_dict['p{}_organisations'.format(x)], separator="\n")
                abstract = unicode(entry_dict['p{}_abstract'.format(x)], 'utf-8')
                try:
                    start = strptime(entry_dict['p{}_start'.format(x)], "%Y-%m-%d %H:%M")
                    end = strptime(entry_dict['p{}_end'.format(x)], "%Y-%m-%d %H:%M")
                except:
                    start = None
                    end = None
                self.contributions.append(Contribution(authors=authors,
                                                       title=title,
                                                       organizations=organizations,
                                                       abstract=abstract,
                                                       type=self.type,
                                                       start=start,
                                                       end=end,
                                                       emails=emails)) #TODO

            else:
                break # empty tile --> last talk of session

        # sort contribution by time
        self.contributions.sort(key=lambda x: x.start, reverse=False)


    @property
    def start_str(self):
        return strftime("%H:%M", self.start)

    @property
    def end_str(self):
        return strftime("%H:%M", self.end)

    @property
    def day(self):
        return strftime("%d", self.start)

    @property
    def weekday(self):
        return strftime("%A", self.start)

    @property
    def smallest_conf_id(self):
        try:
            return min([x.conf_id for x in self.contributions])
        except:
            return None

    @property
    def largets_conf_id(self):
        try:
            return max([x.conf_id for x in self.contributions])
        except:
            return None



# ============================================

class Conference():
    """basically a ordered dict{day} of dict{time} of dict{room} all sessions"""

    def __init__(self, sessions_csv):
        s_dict = {}
        print("processing: " + sessions_csv)
        self.file = sessions_csv
        self.file_hash = secure_hash(self.file)
        with open(sessions_csv, 'rb') as csvfile:
            for row in DictReader(csvfile, delimiter=',', quotechar='"'):
                session = Session(entry_dict=row)
                day = session.day
                if not s_dict.has_key(day):
                    s_dict[day] = {}
                if not s_dict[day].has_key(session.start_str):
                    s_dict[day][session.start_str] = {}
                if s_dict[day][session.start_str].has_key(session.room):
                    raise RuntimeError("TIME CONFLICT")

                s_dict[day][session.start_str][session.room] = session

        ## sort dict
        s_dict = OrderedDict(sorted(s_dict.items())) # sort days
        for x in s_dict.keys():
            s_dict[x] = OrderedDict(sorted(s_dict[x].items())) # sort time
            for y in s_dict[x]:
                s_dict[x][y] = OrderedDict(sorted(s_dict[x][y].items())) # sort room

        self._session_dict = s_dict

        ## make_conference_ids
        poster_cnt = 0
        talk_cnt = 0
        for d in self.get_day_ids():
            poster_cnt += ((talk_cnt/1000)+1)*1000
            for t in self.get_times(d):
                for r in self.get_rooms(d, t):
                    session = self.get_session(d,t,r)
                    for x in session.contributions:
                        if session.type=="poster":
                            poster_cnt += 1
                            x.conf_id = poster_cnt
                        else:
                            talk_cnt += 1
                            x.conf_id = talk_cnt

    def get_day_ids(self):
        return self._session_dict.keys()

    def get_times(self, day):
        return self._session_dict[day].keys()

    def get_rooms(self, day, time):
        return self._session_dict[day][time].keys()

    def get_session(self, day, time, room):
        try:
            return self._session_dict[day][time][room]
        except:
            return None

    def get_latest_end_time(self, day, time):
        latest_end = gmtime(0)
        for session in self._session_dict[day][time].values():
            if latest_end < session.end:
                latest_end = session.end
        return strftime("%H:%M", latest_end)

    def get_all_sessions_at_day(self, day, noposter=False):
        rtn = []
        for time in self.get_times(day):
            rtn.extend(self._session_dict[day][time].values())

        rtn.sort(key=lambda x: x.smallest_conf_id)
        if noposter:
            rtn = filter(lambda x: x.type!="poster", rtn)

        return rtn

    def get_all_rooms(self, noposter=True):
        # all rooms at the conference
        rtn = []
        for d in self.get_day_ids():
            rtn.extend([x.room for x in self.get_all_sessions_at_day(d, noposter)])
        return sorted(list(set(rtn)))

