# coding: utf-8
from __future__ import print_function, unicode_literals

import os

from .__init__ import TYPE_CHECKING
from .authsrv import VFS
from .bos import bos
from .th_srv import HAVE_WEBP, thumb_path
from .util import Cooldown

if True:  # pylint: disable=using-constant-test
    from typing import Optional, Union

if TYPE_CHECKING:
    from .httpsrv import HttpSrv


class ThumbCli(object):
    def __init__(self, hsrv: "HttpSrv") -> None:
        self.broker = hsrv.broker
        self.log_func = hsrv.log
        self.args = hsrv.args
        self.asrv = hsrv.asrv

        # cache on both sides for less broker spam
        self.cooldown = Cooldown(self.args.th_poke)

        try:
            c = hsrv.th_cfg
            if not c:
                raise Exception()
        except:
            c = {k: set() for k in ["thumbable", "pil", "vips", "ffi", "ffv", "ffa"]}

        self.thumbable = c["thumbable"]
        self.fmt_pil = c["pil"]
        self.fmt_vips = c["vips"]
        self.fmt_ffi = c["ffi"]
        self.fmt_ffv = c["ffv"]
        self.fmt_ffa = c["ffa"]

        # defer args.th_ff_jpg, can change at runtime
        d = next((x for x in self.args.th_dec if x in ("vips", "pil")), None)
        self.can_webp = HAVE_WEBP or d == "vips"

    def log(self, msg: str, c: Union[int, str] = 0) -> None:
        self.log_func("thumbcli", msg, c)

    def get(self, dbv: VFS, rem: str, mtime: float, fmt: str) -> Optional[str]:
        ptop = dbv.realpath
        ext = rem.rsplit(".")[-1].lower()
        if ext not in self.thumbable or "dthumb" in dbv.flags:
            return None

        is_vid = ext in self.fmt_ffv
        if is_vid and "dvthumb" in dbv.flags:
            return None

        want_opus = fmt in ("opus", "caf", "mp3")
        is_au = ext in self.fmt_ffa
        is_vau = want_opus and ext in self.fmt_ffv
        if is_au or is_vau:
            if want_opus:
                if self.args.no_acode:
                    return None
            else:
                if "dathumb" in dbv.flags:
                    return None
        elif want_opus:
            return None

        is_img = not is_vid and not is_au
        if is_img and "dithumb" in dbv.flags:
            return None

        preferred = self.args.th_dec[0] if self.args.th_dec else ""

        if rem.startswith(".hist/th/") and rem.split(".")[-1] in ["webp", "jpg", "png"]:
            return os.path.join(ptop, rem)

        if fmt[:1] in "jw":
            sfmt = fmt[:1]

            if sfmt == "j" and self.args.th_no_jpg:
                sfmt = "w"

            if sfmt == "w":
                if (
                    self.args.th_no_webp
                    or (is_img and not self.can_webp)
                    or (self.args.th_ff_jpg and (not is_img or preferred == "ff"))
                ):
                    sfmt = "j"

            vf_crop = dbv.flags["crop"]
            vf_th3x = dbv.flags["th3x"]

            if "f" in vf_crop:
                sfmt += "f" if "n" in vf_crop else ""
            else:
                sfmt += "f" if "f" in fmt else ""

            if "f" in vf_th3x:
                sfmt += "3" if "y" in vf_th3x else ""
            else:
                sfmt += "3" if "3" in fmt else ""

            fmt = sfmt

        elif fmt[:1] == "p" and not is_au and not is_vid:
            t = "cannot thumbnail %r: png only allowed for waveforms"
            self.log(t % (rem,), 6)
            return None

        histpath = self.asrv.vfs.histtab.get(ptop)
        if not histpath:
            self.log("no histpath for %r" % (ptop,))
            return None

        tpath = thumb_path(histpath, rem, mtime, fmt, self.fmt_ffa)
        tpaths = [tpath]
        if fmt == "w":
            # also check for jpg (maybe webp is unavailable)
            tpaths.append(tpath.rsplit(".", 1)[0] + ".jpg")

        ret = None
        abort = False
        for tp in tpaths:
            try:
                st = bos.stat(tp)
                if st.st_size:
                    ret = tpath = tp
                    fmt = ret.rsplit(".")[1]
                    break
                else:
                    abort = True
            except:
                pass

        if ret:
            tdir = os.path.dirname(tpath)
            if self.cooldown.poke(tdir):
                self.broker.say("thumbsrv.poke", tdir)

            if want_opus:
                # audio files expire individually
                if self.cooldown.poke(tpath):
                    self.broker.say("thumbsrv.poke", tpath)

            return ret

        if abort:
            return None

        if not bos.path.getsize(os.path.join(ptop, rem)):
            return None

        x = self.broker.ask("thumbsrv.get", ptop, rem, mtime, fmt)
        return x.get()  # type: ignore
