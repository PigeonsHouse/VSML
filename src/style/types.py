from __future__ import annotations

import re
from enum import Enum, auto

from definition import COLOR_LIST, COLOR_VALUE, REAL_NUMBER_PATTERN
from utils import VSMLManager


class Order(Enum):
    SEQUENCE = auto()
    PARALLEL = auto()

    def __str__(self) -> str:
        return "'{}'".format(self.name)

    def __repr__(self) -> str:
        return "'{}'".format(self.name)


class LayerMode(Enum):
    SINGLE = auto()
    MULTI = auto()

    def __str__(self) -> str:
        return "'{}'".format(self.name)

    def __repr__(self) -> str:
        return "'{}'".format(self.name)


class AudioSystem(Enum):
    MONAURAL = auto()
    STEREO = auto()

    def __str__(self) -> str:
        return "'{}'".format(self.name)

    def __repr__(self) -> str:
        return "'{}'".format(self.name)


class TimeUnit(Enum):
    PERCENT = auto()
    FRAME = auto()
    SECOND = auto()
    FIT = auto()
    SOURCE = auto()

    def __str__(self) -> str:
        match self.name:
            case self.PERCENT.name:
                return "%"
            case self.FRAME.name:
                return "f"
            case self.SECOND.name:
                return "s"
            case self.FIT.name:
                return "fit"
            case self.SOURCE.name:
                return "source"
            case _:
                return ""

    def __repr__(self) -> str:
        match self.name:
            case self.PERCENT.name:
                return "%"
            case self.FRAME.name:
                return "f"
            case self.SECOND.name:
                return "s"
            case self.FIT.name:
                return "fit"
            case self.SOURCE.name:
                return "source"
            case _:
                return ""


class GraphicUnit(Enum):
    AUTO = auto()
    PERCENT = auto()
    PIXEL = auto()
    RESOLUTION_WIDTH = auto()
    RESOLUTION_HEIGHT = auto()
    RESOLUTION_MIN = auto()
    RESOLUTION_MAX = auto()

    def __str__(self) -> str:
        match self.name:
            case self.AUTO.name:
                return "auto"
            case self.PERCENT.name:
                return "%"
            case self.PIXEL.name:
                return "px"
            case self.RESOLUTION_WIDTH.name:
                return "rw"
            case self.RESOLUTION_HEIGHT.name:
                return "rh"
            case self.RESOLUTION_MIN.name:
                return "rmin"
            case self.RESOLUTION_MAX.name:
                return "rmax"
            case _:
                return ""

    def __repr__(self) -> str:
        match self.name:
            case self.AUTO.name:
                return "auto"
            case self.PERCENT.name:
                return "%"
            case self.PIXEL.name:
                return "px"
            case self.RESOLUTION_WIDTH.name:
                return "rw"
            case self.RESOLUTION_HEIGHT.name:
                return "rh"
            case self.RESOLUTION_MIN.name:
                return "rmin"
            case self.RESOLUTION_MAX.name:
                return "rmax"
            case _:
                return ""


class ColorType(Enum):
    PURE = auto()
    HEX = auto()


class TimeValue:
    value: float
    unit: TimeUnit

    def __init__(self, val: str) -> None:
        if val == "fit":
            self.unit = TimeUnit.FIT
            self.value = -1
        elif val == "source":
            self.unit = TimeUnit.SOURCE
            self.value = -1
        elif val == "0":
            self.unit = TimeUnit.FRAME
            self.value = 0
        else:
            match val[-1:]:
                case "s":
                    self.unit = TimeUnit.SECOND
                case "f":
                    self.unit = TimeUnit.FRAME
                case "%":
                    self.unit = TimeUnit.PERCENT
                case _:
                    raise ValueError()
            self.value = float(val[:-1])

    def __str__(self) -> str:
        match self.unit:
            case TimeUnit.FIT | TimeUnit.SOURCE:
                return "'{}'".format(self.unit)
            case _:
                return "'{}{}'".format(self.value, self.unit)

    def __repr__(self) -> str:
        match self.unit:
            case TimeUnit.FIT | TimeUnit.SOURCE:
                return "'{}'".format(self.unit)
            case _:
                return "'{}{}'".format(self.value, self.unit)

    def __lt__(self, other: TimeValue) -> bool:
        return self.get_second() < other.get_second()

    def __add__(self, other: TimeValue) -> TimeValue:
        second = self.get_second() + other.get_second()
        return TimeValue(f"{second}s")

    def __iadd__(self, other: TimeValue) -> TimeValue:
        return self + other

    def get_second(self, default_value: float = 0) -> float:
        if self.unit == TimeUnit.SECOND:
            return self.value
        elif self.unit == TimeUnit.FRAME:
            return self.value / VSMLManager.get_root_fps()
        else:
            return default_value

    def is_zero_over(self) -> bool:
        if self.unit in [TimeUnit.SECOND, TimeUnit.FRAME, TimeUnit.PERCENT]:
            return self.value > 0
        else:
            return False

    def is_fit(self) -> bool:
        return self.unit == TimeUnit.FIT

    def has_specific_value(self) -> bool:
        return self.unit in [TimeUnit.SECOND, TimeUnit.FRAME]


class GraphicValue:
    value: int
    unit: GraphicUnit

    def __init__(self, val: str) -> None:
        if val == "auto":
            self.unit = GraphicUnit.AUTO
            self.value = -1
        elif val[-2:] == "px":
            self.unit = GraphicUnit.PIXEL
            self.value = int(val[:-2])
        elif val[-2:] == "rw":
            self.unit = GraphicUnit.RESOLUTION_WIDTH
            self.value = int(val[:-2])
        elif val[-2:] == "rh":
            self.unit = GraphicUnit.RESOLUTION_HEIGHT
            self.value = int(val[:-2])
        elif val[-4:] == "rmin":
            self.unit = GraphicUnit.RESOLUTION_MIN
            self.value = int(val[:-4])
        elif val[-4:] == "rmax":
            self.unit = GraphicUnit.RESOLUTION_MAX
            self.value = int(val[:-4])
        elif val[-1:] == "%":
            self.unit = GraphicUnit.PERCENT
            self.value = int(val[:-1])
        elif val == "0":
            self.unit = GraphicUnit.PIXEL
            self.value = 0
        else:
            raise ValueError()

    def __str__(self) -> str:
        match self.unit:
            case GraphicUnit.AUTO:
                return "'{}'".format(self.unit)
            case _:
                return "'{}{}'".format(self.value, self.unit)

    def __repr__(self) -> str:
        match self.unit:
            case GraphicUnit.AUTO:
                return "'{}'".format(self.unit)
            case _:
                return "'{}{}'".format(self.value, self.unit)

    def __lt__(self, other: GraphicValue) -> bool:
        return self.get_pixel() < other.get_pixel()

    def __add__(self, other: GraphicValue) -> GraphicValue:
        pixel = self.get_pixel() + other.get_pixel()
        return GraphicValue(f"{pixel}px")

    def __sub__(self, other: GraphicValue) -> GraphicValue:
        pixel = self.get_pixel() - other.get_pixel()
        return GraphicValue(f"{pixel}px")

    def __neg__(self) -> GraphicValue:
        self.value *= -1
        return self

    def get_pixel(self, default_value: int = 0) -> int:
        return self.value if self.unit == GraphicUnit.PIXEL else default_value

    def is_zero_over(self) -> bool:
        if self.unit in [GraphicUnit.PERCENT, GraphicUnit.PIXEL]:
            return self.value > 0
        else:
            return False

    def is_auto(self) -> bool:
        return self.unit == GraphicUnit.AUTO

    def has_specific_value(self) -> bool:
        return self.unit == GraphicUnit.PIXEL


class Color:
    value: str
    type: ColorType
    r_value: int
    g_value: int
    b_value: int
    a_value: int

    def __init__(self, val: str) -> None:
        self.a_value = 255

        if val in COLOR_LIST:
            self.value = val
            self.type = ColorType.PURE
            self.r_value, self.g_value, self.b_value = COLOR_VALUE.get(
                val, [0, 0, 0]
            )
        elif val[0] == "#":
            self.type = ColorType.HEX
            hex_val = val[1:]
            match len(hex_val):
                case 3:
                    self.value = "#{0}{0}{1}{1}{2}{2}".format(
                        hex_val[0], hex_val[1], hex_val[2]
                    )
                case 4:
                    self.value = "#{0}{0}{1}{1}{2}{2}{3}{3}".format(
                        hex_val[0], hex_val[1], hex_val[2], hex_val[3]
                    )
                case 6 | 8:
                    self.value = val
            if len(self.value) == 7:
                self.r_value = int(self.value[1:3], 16)
                self.g_value = int(self.value[3:5], 16)
                self.b_value = int(self.value[5:7], 16)
            elif len(self.value) == 9:
                self.r_value = int(self.value[1:3], 16)
                self.g_value = int(self.value[3:5], 16)
                self.b_value = int(self.value[5:7], 16)
                self.a_value = int(self.value[7:9], 16)
        elif val[:4] == "rgb(":
            self.type = ColorType.HEX
            find_val = re.findall(
                r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)",
                val,
            )
            if len(find_val) > 0:
                r, g, b = find_val[0]
                self.r_value = int(r)
                self.g_value = int(g)
                self.b_value = int(b)
                self.value = "#{}{}{}".format(
                    format(self.r_value, "x").zfill(2),
                    format(self.g_value, "x").zfill(2),
                    format(self.b_value, "x").zfill(2),
                )
        elif val[:5] == "rgba(":
            self.type = ColorType.HEX
            find_val = re.findall(
                r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,"
                r"\s*(\d+)\s*,\s*([{0}]+)\s*\)".format(REAL_NUMBER_PATTERN),
                val,
            )
            if len(find_val) > 0:
                r, g, b, a = find_val[0]
                self.r_value = int(r)
                self.g_value = int(g)
                self.b_value = int(b)
                self.a_value = int(float(a) % 1.0 * 255)
                self.value = "#{}{}{}{}".format(
                    format(self.r_value, "x").zfill(2),
                    format(self.g_value, "x").zfill(2),
                    format(self.b_value, "x").zfill(2),
                    format(self.a_value, "x").zfill(2),
                )
        else:
            raise ValueError()

    def __str__(self) -> str:
        return "'{}'".format(self.value)

    def __repr__(self) -> str:
        return "'{}'".format(self.value)


class Direction(Enum):
    ROW = auto()
    COLUMN = auto()

    def __str__(self) -> str:
        match self:
            case self.ROW:
                return "ROW"
            case self.COLUMN:
                return "COLUMN"
            case _:
                return ""

    def __repr__(self) -> str:
        match self:
            case self.ROW:
                return "ROW"
            case self.COLUMN:
                return "COLUMN"
            case _:
                return ""


class DirectionInfo:
    direction: Direction
    is_reverse: bool

    def __init__(self, val: str) -> None:
        match val:
            case "row":
                self.direction = Direction.ROW
                self.is_reverse = False
            case "column":
                self.direction = Direction.COLUMN
                self.is_reverse = False
            case "row-reverse":
                self.direction = Direction.ROW
                self.is_reverse = True
            case "column-reverse":
                self.direction = Direction.COLUMN
                self.is_reverse = True
            case _:
                raise ValueError()

    def is_row(self) -> bool:
        return self.direction == Direction.ROW

    def __str__(self) -> str:
        if self.is_reverse:
            return "'{}_REVERSE'".format(self.direction)
        return "'{}'".format(self.direction)

    def __repr__(self) -> str:
        if self.is_reverse:
            return "'{}_REVERSE'".format(self.direction)
        return "'{}'".format(self.direction)
