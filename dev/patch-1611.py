#!/usr/bin/env python3
"""FamTM 1.6.11 - an age turns on the birthday, and a second birthday can be written down.

The age was the year of birth taken off the current year, so everybody whose birthday is still to
come read a year older than they are: somebody born in December 1986 read 40 all through the year
they were 39. It is now the whole years actually lived, so it changes on the day.

And a person can carry a second birthday - the date on a passport or another paper, when it is not
the same day as the real one - beside the born date.

    python3 dev/patch-1611.py            # apply
    python3 dev/patch-1611.py --check    # verify only, writes nothing
"""

import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGE = "app/src/main/assets/index.html"

V = "1.6.11"
OLD = "1.6.10"

AGE_OLD = """const age=p=>{const b=parseInt(yr(p.birth)||'0');if(!b)return'';const dy=parseInt(yr(p.death)||'0');if(p.death&&!dy)return'';
 const n=(dy||new Date().getFullYear())-b;return n>=0?(p.death?'Lived ':'Age ')+n:''};
"""

AGE_NEW = """// 1.6.11 - an age is the whole years lived, so it turns on the birthday and not on 1 January.
// Somebody born in December 1986 read 40 all through the year they were 39, because the year of
// birth was simply taken off the current year.
const dp=d=>{const s=str(d);
 let m=/^([0-9]{4})(?:-([0-9]{2})(?:-([0-9]{2}))?)?$/.exec(s);
 if(m)return{y:+m[1],m:m[2]?+m[2]:0,d:m[3]?+m[3]:0};
 m=/^--([0-9]{2})(?:-([0-9]{2}))?$/.exec(s);
 return m?{y:0,m:+m[1],d:m[2]?+m[2]:0}:null};
// Whole years from one date to another. Only a date known to the day can say whether the birthday
// has been yet: a year alone, or a month with no day, leaves the count where the years put it.
const yrs=(a,b)=>{const x=dp(a),z=dp(b);if(!x||!x.y||!z||!z.y)return null;
 let n=z.y-x.y;
 if(x.m&&x.d&&(z.m<x.m||(z.m===x.m&&z.d<x.d)))n-=1;
 return n};
const dayNow=()=>{const t=new Date(),z=n=>('0'+n).slice(-2);return t.getFullYear()+'-'+z(t.getMonth()+1)+'-'+z(t.getDate())};
const age=p=>{if(!yr(p.birth))return'';if(p.death&&!yr(p.death))return'';
 const n=yrs(p.birth,p.death||dayNow());
 return n==null||n<0?'':(p.death?'Lived ':'Age ')+n};
"""

NORM_OLD = "birth:str(o.birth),death:str(o.death),note:str(o.note)"
NORM_NEW = "birth:str(o.birth),...(str(o.birth2)?{birth2:str(o.birth2)}:{}),death:str(o.death),note:str(o.note)"

FORM_OLD = """ <div class="g2"><label>Born<input id="fb" value="${h(fmt(p.birth))}"></label><label>Died<input id="fd" value="${h(fmt(p.death))}" placeholder="blank if living"></label></div>
"""

FORM_NEW = """ <div class="g2"><label>Born<input id="fb" value="${h(fmt(p.birth))}"></label><label>Died<input id="fd" value="${h(fmt(p.death))}" placeholder="blank if living"></label></div>
 <div class="g2"><label>Second birthday<input id="fb2" value="${h(fmt(p.birth2))}" placeholder="optional"></label><span></span></div><p class="m" style="margin:-2px 0 8px">Only when it is not the same day: the date on a passport or another paper, kept beside the real one. An age is counted from the birthday above, not from this.</p>
"""

READ_OLD = "const b=normDate($('#fb').value),d=normDate($('#fd').value);\n"
READ_NEW = "const b=normDate($('#fb').value),d=normDate($('#fd').value),b2=normDate($('#fb2').value);\n"

BAD_OLD = "b===null||d===null?"
BAD_NEW = "b===null||d===null||b2===null?"

ASSIGN_OLD = "if(ph)o.photo=ph;else delete o.photo;"
ASSIGN_NEW = "if(ph)o.photo=ph;else delete o.photo;if(b2)o.birth2=b2;else delete o.birth2;"

DETAIL_OLD = "[p.birth&&'Born '+fmt(p.birth),p.death&&'Died '+fmt(p.death),age(p)]"
DETAIL_NEW = ("[p.birth&&'Born '+fmt(p.birth),p.birth2&&'Second birthday '+fmt(p.birth2),"
              "p.death&&'Died '+fmt(p.death),age(p)]")

ENTRY = """{"v":"1.6.11","d":"2026-11-12","t":"An age turns on the birthday, and a second birthday has a box","x":[\
"An age is counted in the years actually lived now, so it changes on the birthday instead of on the 1st of January. It was the year of birth taken off the current year, which made everyone whose birthday is still to come a year older than they are: somebody born in December 1986 read <b>Age 40</b> all through the year they were 39. They read 39 until their birthday, and 40 from that morning.\
","The same is true of someone who has died: <b>Lived</b> is now the age they reached, counted to the day of the death, not the difference between two years. A born date with only a year, or a year and a month, cannot say whether the birthday had come, so those are counted by the year as before - the page never guesses a day it was not given.\
","A second birthday has a box of its own under Born and Died, for the date written on a passport or another paper when it is not the same day as the real one. It is shown on the person's page beside their dates as <i>Second birthday 4 Jul 1986</i>, it is saved with them, and it travels in a backup like every other date - a backup from this version restores into the one before it and the other way round, because a person without one is stored exactly as before.\
","It does not touch the age or the birthday reminder: an age is counted from the real birthday, and the notification still arrives on that day. The second date is only ever a note of what a paper says.\
"]},"""


def read(rel):
    with io.open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def write(rel, text):
    with io.open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="") as f:
        f.write(text)


def one(text, old, what):
    if text.count(old) != 1:
        sys.exit("patch-1611: %s appears %d times, expected exactly 1" % (what, text.count(old)))
    return text


def patched(page):
    if ("const VER='%s'" % V) in page and "id=\"fb2\"" in page:
        return page
    one(page, "const VER='%s'" % OLD, "the version")
    one(page, AGE_OLD, "the age function")
    one(page, NORM_OLD, "normPerson's dates")
    one(page, FORM_OLD, "the Born/Died row")
    one(page, READ_OLD, "the form's date reading")
    one(page, BAD_OLD, "the date check")
    one(page, ASSIGN_OLD, "the photo assignment")
    one(page, DETAIL_OLD, "the dates on a person's page")
    one(page, '[{"v":"%s"' % OLD, "the top of the What's New list")
    out = page.replace("const VER='%s'" % OLD, "const VER='%s'" % V, 1)
    out = out.replace(AGE_OLD, AGE_NEW, 1)
    out = out.replace(NORM_OLD, NORM_NEW, 1)
    out = out.replace(FORM_OLD, FORM_NEW, 1)
    out = out.replace(READ_OLD, READ_NEW, 1)
    out = out.replace(BAD_OLD, BAD_NEW, 1)
    out = out.replace(ASSIGN_OLD, ASSIGN_NEW, 1)
    out = out.replace(DETAIL_OLD, DETAIL_NEW, 1)
    return out.replace('[{"v":"%s"' % OLD, "[" + ENTRY + '{"v":"%s"' % OLD, 1)


def main():
    check = "--check" in sys.argv
    page = read(PAGE)
    new = patched(page)
    if new == page:
        print("already on the page")
        return 0
    if check:
        print("not applied yet")
        return 1
    write(PAGE, new)
    print("page at v%s, second birthday on the form, ages counted by date" % V)
    return 0


if __name__ == "__main__":
    sys.exit(main())
