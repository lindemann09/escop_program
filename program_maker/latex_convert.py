from unicode_tex import tex_args, unicode_to_tex

# helper
def plain_name(surname_comma_first_name):
    # converts <surname>, <fist name> to <fist name> <surname>
    x = surname_comma_first_name.split(',')
    return x[1].strip() + " " + x[0].strip()

def punctuation(txt):
    # appends punctuation mark, if txt doesn't end with a punctuation

    if txt[-1] not in u"!#%&()*+,-.:;=?":
        return txt + "."
    return txt


def contribution_list(conference, filename, list_contributions=True, talks_first=False):
    # conference: conference_structure.Conference

    txt = u"%%%% CONTRIBUTION LIST \n"
    txt += u"%% file: {} (sha1: {}) \n".format(conference.file, conference.file_hash)
    for d in conference.get_day_ids():
        weekday = conference.get_all_sessions_at_day(d)[0].weekday
        txt += u"\n\n\\overviewdaybegin{" + weekday + ", " + str(d) + " September 2017}\n"
        
        poster = u""
        talks = u""
        for t in conference.get_times(d):
            newtime_begin_required = True
            tmptxt = u""
            for r in conference.get_rooms(d, t):
                session = conference.get_session(d, t, r)
                if newtime_begin_required:
                    if session.type == "poster":
                        tmptxt += u"\n\\overviewtimeslotbegin" + tex_args(t, session.end_str,
                                session.title[:session.title.find("-")].strip()) + "\n"
                    else:
                        tmptxt += u"\n\\overviewtimeslotbegin" + tex_args(t, session.end_str, "Talks & Symposia") + "\n"
                    newtime_begin_required = False

                if session.type == "poster":
                    tmptxt += u"\\overviewposterbegin{}\n"
                else:
                    if session.type == "symposium":
                        type_txt = "Symposium"
                        if len(session.chair) > 0:
                            info_code = u"{\\newline{\\itshape Organized by " + unicode_to_tex(plain_name(session.chair)) + u"}}"
                        else:
                            info_code = u"{}"
                    else:
                        type_txt = ""
                        if len(session.chair) > 0:
                            info_code = u"{\\newline{\\itshape Chaired by " + unicode_to_tex(plain_name(session.chair)) + u"}}"
                        else:
                            info_code = u"{}"

                    tmptxt += u"\n\\overviewsessionbegin" + tex_args(u"{}-{}".format(session.smallest_conf_id, session.largets_conf_id),
                                                                 type_txt, session.room,
                                                                 session.title) + info_code +"\n"
                if (list_contributions):
                    for c in session.contributions:
                        if c.type == "poster":
                            tmptxt += u"    \\postershort" + tex_args(c.conf_id,
                                                                   punctuation(c.formated_authors(fullnames=False, first_name_initials=False)),
                                                                   punctuation(c.title)) +"\n"
                        else:
                            tmptxt += u"    \\talkshort" + tex_args(c.conf_id, c.start_str, c.end_str,
                                                                 punctuation(c.formated_authors(fullnames=False, first_name_initials=False)),
                                                                 punctuation(c.title)) + "\n"
                if session.type == "poster":
                    tmptxt += u"\overviewposterend{}\n\n"
                else:
                    tmptxt += u"\overviewsessionend{}\n\n"

            tmptxt += u"\n\\overviewtimeslotend{}\n"
            if talks_first:
                if session.type == "poster": # last session type
                    poster += tmptxt
                else:
                    talks += tmptxt
            else:
                txt += tmptxt

        if talks_first:
            txt += talks + poster
        txt += u"\n\n\\overviewdayend{}\n"

    print("writing: " + filename)
    with open(filename, "wb") as f:
       f.write(txt.encode("UTF-8"))



def abstracts(conference, filename, write_index=False):
    # conference: conference_structure.Conference

    poster = u""
    talks = u""
    for d in conference.get_day_ids():
        for session in conference.get_all_sessions_at_day(d):
            txt = u""
            session_time = u"{0}, {1} -- {2}".format(session.weekday, session.start_str, session.end_str)

            if session.type == "poster":
                txt += u"\n\\abstractposterbegin" + tex_args(session_time, session.room,
                                                               session.title[:session.title.find("-")].strip()) + "\n"
            else:
                if session.type == "symposium":
                    tmp = "Symposium: " + session.title
                else:
                    tmp = session.title
                txt += u"\n\\abstractsessionbegin" + tex_args(session_time,session.room, tmp) + "\n"

            for c in session.contributions:
                if session.type == "poster":
                    start_time = ""
                else:
                    start_time = u"{0} -- {1}".format(c.start_str, c.end_str)
                txt += u"    \\escopabstract" + tex_args(c.conf_id, start_time) + \
                                        u"{" + c.formated_authors(fullnames=True, first_name_initials=False,
                                                                  affiliation_ids=True,
                                                                  orga_id_format=u"$^{{{0}}}$",
                                                                  tex_code=True,
                                                                  write_index=write_index) + u"}" + \
                                        u"{" + c.formated_organisations(orga_id_format=u"$^{{{0}}}$", tex_code=True) + u"}" + \
                                        tex_args(punctuation(c.title), c.abstract, c.first_author_email) + "\n\n"

            txt += u"\\abstractsessionend{}\n\n"
            if session.type == "poster":
                poster += txt
            else:
                talks += txt

    txt = u"%%%% ABSTRACTS\n"
    txt += u"%% file: {} (sha1: {}) \n".format(conference.file,
                                                conference.file_hash)
    txt += talks + poster

    print("writing: " + filename)
    with open(filename, "wb") as f:
       f.write(txt.encode("UTF-8"))


def overview_table_code(conference, filename):
    # conference: conference_structure.Conference

    rooms = conference.get_all_rooms(noposter=True)
    cmddict = {}
    for dn, d in enumerate(conference.get_day_ids()):
        day = u"day" + chr(65+dn)
        cmddict[day] = conference.get_all_sessions_at_day(d)[0].weekday + ", " + \
                        str(d) + " September 2017"



        #set room and sessiona to NONE
        for cnt, r in enumerate(rooms):
            room = u"room" + chr(65 + cnt)
            cmddict[day + room] = r
            for tn, t in enumerate(conference.get_times(d)):
                time = u"time" + chr(65 + tn)
                cmddict[day + room + time] = ""

        for tn, t in enumerate(conference.get_times(d)):
            time = u"time" + chr(65 + tn)
            end = conference.get_latest_end_time(d,t)
            cmddict[day+time] = u"{0} -- {1}".format(t,end)
            poster_rooms = u", ".join(conference.get_rooms(d, t))
            x = poster_rooms.rfind(",")
            poster_rooms = unicode_to_tex(poster_rooms[:x] + " &" + poster_rooms[(x+1):])
            for r in conference.get_rooms(d, t):
                session = conference.get_session(d, t, r)
                if session.type == "poster":
                    cmddict[day + "poster" + time] = "{ " + session.title[:session.title.find(" - ")].strip() + \
                        "}\\par {\\itshape Rooms: " + poster_rooms + "}"
                else:
                    # shorten title with subtitle (: -)
                    tmp = session.title
                    x = max([tmp.find(":"), tmp.find(" - ")])
                    if x>0:
                        tmp = tmp[:x]
                    if session.type == "symposium":
                        tmp = u"(S) " + tmp
                    tmp += u" \\par{{\\itshape ({} -- {})}}".format(session.smallest_conf_id, session.largets_conf_id)
                    room = u"room" + chr(65 + rooms.index(session.room))
                    cmddict[day + room + time] = tmp

    # cmddict to text
    txt = u"%%%% OVERVIEW TABLE COMMANDS\n"
    txt += u"%% file: {} (sha1: {}) \n".format(conference.file,
                                                conference.file_hash)
    for k,v in cmddict.iteritems():
        txt += u"\\newcommand{{\\{0}}}{{{1}}}\n".format(k,v)

    print("writing: " + filename)
    with open(filename, "wb") as f:
       f.write(txt.encode("UTF-8"))
