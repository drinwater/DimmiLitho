"""

"""

import math

import jax.numpy as np
from scipy.special import erf


def Edeta(deta, x):
    if deta != 0:
        g = 0.5 * (1 + erf(x / deta))
        return g
    else:
        g = np.zeros(x.shape)
        g[x >= 0] = 1
        return g


class Source:
    """
    Source.data is used for Abbe fomulation
    Source.mdata is used for Hopkins fomulation, Mutual Intensity, TCC calculation

    """

    def __init__(
        self,
        na=1.35,
        wavelength=193.0,
        maskxpitch=2000.0,
        maskypitch=2000.0,
        sigma_out=0.8,
        sigma_in=0.6,
        smooth_deta=0.03,
        shiftAngle=math.pi / 4,
        openAngle=math.pi / 16,
        source_type="annular",
    ):
        self.na = na
        self.wavelength = wavelength
        self.maskxpitch = maskxpitch
        self.maskypitch = maskypitch

        self.sigma_out = sigma_out
        self.sigma_in = sigma_in
        self.smooth_deta = smooth_deta
        self.shiftAngle = shiftAngle
        self.openAngle = openAngle
        self.type = source_type

    def update(self):
        self.detaf = self.wavelength / (self.maskxpitch * self.na)
        self.detag = self.wavelength / (self.maskypitch * self.na)
        self.fnum = int(np.ceil(2 / self.detaf))
        self.gnum = int(np.ceil(2 / self.detag))

        fx = np.linspace(
            -self.fnum * self.detaf, self.fnum * self.detaf, 2 * self.fnum + 1
        )
        fy = np.linspace(
            -self.gnum * self.detag, self.gnum * self.detag, 2 * self.gnum + 1
        )
        FX, FY = np.meshgrid(fx, fy, indexing="xy")

        r = np.sqrt(FX ** 2 + FY ** 2)
        theta = np.arctan2(FY, FX)
        theta[r > 1] = 0
        r[r > 1] = 0
        s0 = np.sqrt(FX ** 2 + FY ** 2)
        s0[s0 <= 1] = 1
        s0[s0 > 1] = 0

        self.r = r
        self.s0 = s0
        self.theta = theta
        self.fx = FX
        self.fy = FY

        if self.type == "conventional":
            s = Edeta(self.smooth_deta, self.sigma_out - self.r) * self.s0
            self.data = s
        elif self.type == "annular":
            s = (
                Edeta(self.smooth_deta, self.sigma_out - self.r)
                * Edeta(self.smooth_deta, self.r - self.sigma_in)
                * self.s0
            )
            self.data = s
        elif self.type == "quasar":
            s = (
                Edeta(self.smooth_deta, self.sigma_out - self.r)
                * Edeta(self.smooth_deta, self.r - self.sigma_in)
                * (
                    Edeta(
                        self.smooth_deta,
                        self.openAngle
                        - np.abs(1.0 * math.pi - np.abs(self.shiftAngle - self.theta)),
                    )
                    + Edeta(
                        self.smooth_deta,
                        self.openAngle
                        - np.abs(0.5 * math.pi - np.abs(self.shiftAngle - self.theta)),
                    )
                    + Edeta(
                        self.smooth_deta,
                        self.openAngle
                        - np.abs(-0.5 * math.pi - np.abs(self.shiftAngle - self.theta)),
                    )
                    + Edeta(
                        self.smooth_deta,
                        self.openAngle
                        - np.abs(-0.0 * math.pi - np.abs(self.shiftAngle - self.theta)),
                    )
                )
                * self.s0
            )
            self.data = s
        elif self.type == "dipole":
            s = (
                Edeta(self.smooth_deta, self.sigma_out - self.r)
                * Edeta(self.smooth_deta, self.r - self.sigma_in)
                * (
                    Edeta(
                        self.smooth_deta,
                        self.openAngle - np.abs(self.shiftAngle - self.theta),
                    )
                    + Edeta(
                        self.smooth_deta,
                        self.openAngle
                        - np.abs(math.pi - np.abs(self.shiftAngle - self.theta)),
                    )
                )
                * self.s0
            )
            self.data = s
        else:
            s = (
                Edeta(self.smooth_deta, self.sigma_out - self.r)
                * Edeta(self.smooth_deta, self.r - self.sigma_in)
                * self.s0
            )
            self.data = s

    def ifft(self):
        fx = np.linspace(
            -self.fnum * self.detaf, self.fnum * self.detaf, 4 * self.fnum + 1
        )
        fy = np.linspace(
            -self.gnum * self.detag, self.gnum * self.detag, 4 * self.gnum + 1
        )
        FX, FY = np.meshgrid(fx, fy, indexing="xy")

        r = np.sqrt(FX ** 2 + FY ** 2)
        theta = np.arctan2(FY, FX)
        theta[r > 1] = 0
        r[r > 1] = 0
        s0 = np.sqrt(FX ** 2 + FY ** 2)
        s0 = np.where(s0 > 1.0, 0.0, 1.0)

        self.r = r
        self.s0 = s0
        self.theta = theta
        self.fx = FX
        self.fy = FY

        if self.type == "conventional":
            s = Edeta(self.smooth_deta, self.sigma_out - self.r) * self.s0
            self.mdata = s
        elif self.type == "annular":
            s = (
                Edeta(self.smooth_deta, self.sigma_out - self.r)
                * Edeta(self.smooth_deta, self.r - self.sigma_in)
                * self.s0
            )
            self.mdata = s
        elif self.type == "quasar":
            s = (
                Edeta(self.smooth_deta, self.sigma_out - self.r)
                * Edeta(self.smooth_deta, self.r - self.sigma_in)
                * (
                    Edeta(
                        self.smooth_deta,
                        self.openAngle
                        - np.abs(1.0 * math.pi - np.abs(self.shiftAngle - self.theta)),
                    )
                    + Edeta(
                        self.smooth_deta,
                        self.openAngle
                        - np.abs(0.5 * math.pi - np.abs(self.shiftAngle - self.theta)),
                    )
                    + Edeta(
                        self.smooth_deta,
                        self.openAngle
                        - np.abs(-0.5 * math.pi - np.abs(self.shiftAngle - self.theta)),
                    )
                    + Edeta(
                        self.smooth_deta,
                        self.openAngle
                        - np.abs(-0.0 * math.pi - np.abs(self.shiftAngle - self.theta)),
                    )
                )
                * self.s0
            )
            self.mdata = s
        elif self.type == "dipole":
            s = (
                Edeta(self.smooth_deta, self.sigma_out - self.r)
                * Edeta(self.smooth_deta, self.r - self.sigma_in)
                * (
                    Edeta(
                        self.smooth_deta,
                        self.openAngle - np.abs(self.shiftAngle - self.theta),
                    )
                    + Edeta(
                        self.smooth_deta,
                        self.openAngle
                        - np.abs(math.pi - np.abs(self.shiftAngle - self.theta)),
                    )
                )
                * self.s0
            )
            self.mdata = s
        else:
            s = (
                Edeta(self.smooth_deta, self.sigma_out - self.r)
                * Edeta(self.smooth_deta, self.r - self.sigma_in)
                * self.s0
            )
            self.mdata = s
        normlize = 1  # self.detaf * self.detag
        self.spatMutualData = (
            np.fft.fftshift(np.fft.ifft2(np.fft.ifftshift(self.mdata))) * normlize
        )


if __name__ == "__main__":
    s = Source()
    s.type = "annular"
    s.sigma_in = 0.6
    s.sigma_out = 0.8
    s.smooth_deta = 0
    s.update()
    s.ifft()
