from enum import Enum
from typing import List, Dict, Union, Optional, Tuple, Literal
from pydantic import BaseModel, Field, validator


class ChartType(str, Enum):
    CHART = "chart"
    CARD = "card"


class ChartSubtype(str, Enum):
    AREA = "area"
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    RADAR = "radar"


class BarLayout(str, Enum):
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"


class BarType(str, Enum):
    GROUPED = "grouped"
    STACKED = "stacked"


class LineType(str, Enum):
    LINEAR = "linear"
    MONOTONE = "monotone"
    STEP = "step"
    STEP_BEFORE = "stepBefore"
    STEP_AFTER = "stepAfter"
    NATURAL = "natural"
    BASIS = "basis"


class PieLabelType(str, Enum):
    PERCENT = "percent"
    VALUE = "value"
    NAME = "name"
    NAME_PERCENT = "namePercent"


class TrendDirection(str, Enum):
    UP = "up"
    DOWN = "down"


class ValueFormatting(str, Enum):
    NUMBER = "number"
    CURRENCY = "currency"
    PERCENT = "percent"


class DataPoint(BaseModel):
    x: str
    y: float


class Series(BaseModel):
    name: str
    data: List[DataPoint]
    color: Optional[str] = None


class ChartSize(BaseModel):
    cols: Optional[int] = Field(None, ge=1, le=4)
    rows: Optional[int] = Field(None, ge=1, le=4)


class Trend(BaseModel):
    value: float
    direction: TrendDirection
    label: str


class AreaChartOptions(BaseModel):
    show_grid: Optional[bool] = Field(True, alias="showGrid")
    show_legend: Optional[bool] = Field(True, alias="showLegend")
    show_tooltip: Optional[bool] = Field(True, alias="showTooltip")
    y_axis_label: Optional[str] = Field(None, alias="yAxisLabel")
    x_axis_label: Optional[str] = Field(None, alias="xAxisLabel")
    stacked: Optional[bool] = False
    type: Optional[
        Literal["linear", "monotone", "step", "stepBefore", "stepAfter", "natural"]
    ] = "linear"


class BarChartOptions(BaseModel):
    show_grid: Optional[bool] = Field(True, alias="showGrid")
    show_legend: Optional[bool] = Field(True, alias="showLegend")
    show_tooltip: Optional[bool] = Field(True, alias="showTooltip")
    y_axis_label: Optional[str] = Field(None, alias="yAxisLabel")
    x_axis_label: Optional[str] = Field(None, alias="xAxisLabel")
    layout: Optional[BarLayout] = BarLayout.VERTICAL
    bar_type: Optional[BarType] = Field(BarType.GROUPED, alias="barType")
    bar_size: Optional[int] = Field(None, alias="barSize")
    bar_radius: Optional[Union[int, List[int]]] = Field(None, alias="barRadius")


class LineChartOptions(BaseModel):
    show_grid: Optional[bool] = Field(True, alias="showGrid")
    show_legend: Optional[bool] = Field(True, alias="showLegend")
    show_tooltip: Optional[bool] = Field(True, alias="showTooltip")
    y_axis_label: Optional[str] = Field(None, alias="yAxisLabel")
    x_axis_label: Optional[str] = Field(None, alias="xAxisLabel")
    type: Optional[LineType] = LineType.LINEAR
    show_dots: Optional[bool] = Field(True, alias="showDots")
    dot_size: Optional[int] = Field(4, alias="dotSize")
    active_dot_size: Optional[int] = Field(6, alias="activeDotSize")
    stroke_width: Optional[int] = Field(2, alias="strokeWidth")


class PieChartOptions(BaseModel):
    show_legend: Optional[bool] = Field(True, alias="showLegend")
    show_tooltip: Optional[bool] = Field(True, alias="showTooltip")
    inner_radius: Optional[Union[int, str]] = Field(0, alias="innerRadius")
    outer_radius: Optional[Union[int, str]] = Field("90%", alias="outerRadius")
    padding_angle: Optional[float] = Field(0, alias="paddingAngle")
    show_labels: Optional[bool] = Field(True, alias="showLabels")
    label_type: Optional[PieLabelType] = Field(PieLabelType.PERCENT, alias="labelType")


class RadarChartOptions(BaseModel):
    show_grid: Optional[bool] = Field(True, alias="showGrid")
    show_legend: Optional[bool] = Field(True, alias="showLegend")
    show_tooltip: Optional[bool] = Field(True, alias="showTooltip")
    max_value: Optional[float] = Field(None, alias="maxValue")
    fill_opacity: Optional[float] = Field(0.6, alias="fillOpacity")
    stroke_width: Optional[int] = Field(2, alias="strokeWidth")


class ChartConfig(BaseModel):
    type: Literal["chart"] = "chart"
    subtype: ChartSubtype
    header: str
    description: str
    series: List[Series]
    options: Optional[
        Union[
            AreaChartOptions,
            BarChartOptions,
            LineChartOptions,
            PieChartOptions,
            RadarChartOptions,
        ]
    ] = None
    size: Optional[ChartSize] = None

    @validator("options", pre=True)
    def validate_options(cls, v, values):
        # 1) If it's already a Pydantic model, just use it.
        if isinstance(v, BaseModel):
            return v

        # 2) Otherwise v must be a dict, so map by subtype:
        subtype = values.get("subtype")
        if not subtype or not v:
            return v

        subtype = values["subtype"]
        if subtype == ChartSubtype.AREA and v:
            return AreaChartOptions(**v)
        elif subtype == ChartSubtype.BAR and v:
            return BarChartOptions(**v)
        elif subtype == ChartSubtype.LINE and v:
            return LineChartOptions(**v)
        elif subtype == ChartSubtype.PIE and v:
            return PieChartOptions(**v)
        elif subtype == ChartSubtype.RADAR and v:
            return RadarChartOptions(**v)
        return v


class CardConfig(BaseModel):
    type: Literal["card"] = "card"
    header: str
    description: str
    value: Union[float, str]
    value_suffix: Optional[str] = Field(None, alias="valueSuffix")
    value_prefix: Optional[str] = Field(None, alias="valuePrefix")
    value_formatting: Optional[ValueFormatting] = Field(None, alias="valueFormatting")
    icon: Optional[str] = None
    trend: Optional[Trend] = None
    size: Optional[ChartSize] = None


class ChartBuilder:
    @staticmethod
    def create_data_point(x: str, y: float) -> DataPoint:
        """Create a data point for chart series"""
        return DataPoint(x=x, y=y)

    @staticmethod
    def create_series(
        name: str, data_points: List[DataPoint], color: Optional[str] = None
    ) -> Series:
        """Create a data series for charts"""
        return Series(name=name, data=data_points, color=color)

    @staticmethod
    def create_chart_size(
        cols: Optional[int] = None, rows: Optional[int] = None
    ) -> ChartSize:
        """Create chart size configuration"""
        return ChartSize(cols=cols, rows=rows)

    @staticmethod
    def create_trend(value: float, direction: TrendDirection, label: str) -> Trend:
        """Create trend data for metric cards"""
        return Trend(value=value, direction=direction, label=label)

    @classmethod
    def create_area_chart(
        cls,
        header: str,
        description: str,
        series: List[Series],
        show_grid: bool = True,
        show_legend: bool = True,
        show_tooltip: bool = True,
        y_axis_label: Optional[str] = None,
        x_axis_label: Optional[str] = None,
        stacked: bool = False,
        chart_type: str = "linear",
        cols: Optional[int] = None,
        rows: Optional[int] = None,
    ) -> ChartConfig:
        """
        Create an area chart configuration

        Args:
            header: Chart title
            description: Chart description
            series: List of Series objects containing data
            show_grid: Whether to show grid lines
            show_legend: Whether to show the legend
            show_tooltip: Whether to show tooltips on hover
            y_axis_label: Label for the Y axis
            x_axis_label: Label for the X axis
            stacked: Whether to stack the areas
            chart_type: Type of curve ("linear", "monotone", "step", "stepBefore", "stepAfter", "natural")
            cols: Number of columns (1-4) the chart should span
            rows: Number of rows (1-4) the chart should span

        Returns:
            ChartConfig object for an area chart
        """
        options = AreaChartOptions(
            showGrid=show_grid,
            showLegend=show_legend,
            showTooltip=show_tooltip,
            yAxisLabel=y_axis_label,
            xAxisLabel=x_axis_label,
            stacked=stacked,
            type=chart_type,
        )

        size = cls.create_chart_size(cols, rows) if cols or rows else None

        return ChartConfig(
            subtype=ChartSubtype.AREA,
            header=header,
            description=description,
            series=series,
            options=options,
            size=size,
        )

    @classmethod
    def create_bar_chart(
        cls,
        header: str,
        description: str,
        series: List[Series],
        show_grid: bool = True,
        show_legend: bool = True,
        show_tooltip: bool = True,
        y_axis_label: Optional[str] = None,
        x_axis_label: Optional[str] = None,
        layout: BarLayout = BarLayout.VERTICAL,
        bar_type: BarType = BarType.GROUPED,
        bar_size: Optional[int] = None,
        bar_radius: Optional[Union[int, List[int]]] = None,
        cols: Optional[int] = None,
        rows: Optional[int] = None,
    ) -> ChartConfig:
        """
        Create a bar chart configuration

        Args:
            header: Chart title
            description: Chart description
            series: List of Series objects containing data
            show_grid: Whether to show grid lines
            show_legend: Whether to show the legend
            show_tooltip: Whether to show tooltips on hover
            y_axis_label: Label for the Y axis
            x_axis_label: Label for the X axis
            layout: Bar orientation ("vertical" or "horizontal")
            bar_type: Bar grouping ("grouped" or "stacked")
            bar_size: Size of the bars
            bar_radius: Radius for bar corners (single value or [topLeft, topRight, bottomRight, bottomLeft])
            cols: Number of columns (1-4) the chart should span
            rows: Number of rows (1-4) the chart should span

        Returns:
            ChartConfig object for a bar chart
        """
        options = BarChartOptions(
            showGrid=show_grid,
            showLegend=show_legend,
            showTooltip=show_tooltip,
            yAxisLabel=y_axis_label,
            xAxisLabel=x_axis_label,
            layout=layout,
            barType=bar_type,
            barSize=bar_size,
            barRadius=bar_radius,
        )

        size = cls.create_chart_size(cols, rows) if cols or rows else None

        return ChartConfig(
            subtype=ChartSubtype.BAR,
            header=header,
            description=description,
            series=series,
            options=options,
            size=size,
        )

    @classmethod
    def create_line_chart(
        cls,
        header: str,
        description: str,
        series: List[Series],
        show_grid: bool = True,
        show_legend: bool = True,
        show_tooltip: bool = True,
        y_axis_label: Optional[str] = None,
        x_axis_label: Optional[str] = None,
        line_type: LineType = LineType.LINEAR,
        show_dots: bool = True,
        dot_size: int = 4,
        active_dot_size: int = 6,
        stroke_width: int = 2,
        cols: Optional[int] = None,
        rows: Optional[int] = None,
    ) -> ChartConfig:
        """
        Create a line chart configuration

        Args:
            header: Chart title
            description: Chart description
            series: List of Series objects containing data
            show_grid: Whether to show grid lines
            show_legend: Whether to show the legend
            show_tooltip: Whether to show tooltips on hover
            y_axis_label: Label for the Y axis
            x_axis_label: Label for the X axis
            line_type: Type of line curve
            show_dots: Whether to show data points
            dot_size: Size of data points
            active_dot_size: Size of active data points on hover
            stroke_width: Width of the line
            cols: Number of columns (1-4) the chart should span
            rows: Number of rows (1-4) the chart should span

        Returns:
            ChartConfig object for a line chart
        """
        options = LineChartOptions(
            showGrid=show_grid,
            showLegend=show_legend,
            showTooltip=show_tooltip,
            yAxisLabel=y_axis_label,
            xAxisLabel=x_axis_label,
            type=line_type,
            showDots=show_dots,
            dotSize=dot_size,
            activeDotSize=active_dot_size,
            strokeWidth=stroke_width,
        )

        size = cls.create_chart_size(cols, rows) if cols or rows else None

        return ChartConfig(
            subtype=ChartSubtype.LINE,
            header=header,
            description=description,
            series=series,
            options=options,
            size=size,
        )

    @classmethod
    def create_pie_chart(
        cls,
        header: str,
        description: str,
        series: List[Series],
        show_legend: bool = True,
        show_tooltip: bool = True,
        inner_radius: Union[int, str] = 0,
        outer_radius: Union[int, str] = "90%",
        padding_angle: float = 0,
        show_labels: bool = True,
        label_type: PieLabelType = PieLabelType.PERCENT,
        cols: Optional[int] = None,
        rows: Optional[int] = None,
    ) -> ChartConfig:
        """
        Create a pie chart configuration

        Args:
            header: Chart title
            description: Chart description
            series: List of Series objects containing data
            show_legend: Whether to show the legend
            show_tooltip: Whether to show tooltips on hover
            inner_radius: Inner radius for donut charts (0 for pie chart)
            outer_radius: Outer radius of the chart
            padding_angle: Padding angle between slices
            show_labels: Whether to show labels
            label_type: Type of labels to show
            cols: Number of columns (1-4) the chart should span
            rows: Number of rows (1-4) the chart should span

        Returns:
            ChartConfig object for a pie chart
        """
        options = PieChartOptions(
            showLegend=show_legend,
            showTooltip=show_tooltip,
            innerRadius=inner_radius,
            outerRadius=outer_radius,
            paddingAngle=padding_angle,
            showLabels=show_labels,
            labelType=label_type,
        )

        size = cls.create_chart_size(cols, rows) if cols or rows else None

        return ChartConfig(
            subtype=ChartSubtype.PIE,
            header=header,
            description=description,
            series=series,
            options=options,
            size=size,
        )

    @classmethod
    def create_radar_chart(
        cls,
        header: str,
        description: str,
        series: List[Series],
        show_grid: bool = True,
        show_legend: bool = True,
        show_tooltip: bool = True,
        max_value: Optional[float] = None,
        fill_opacity: float = 0.6,
        stroke_width: int = 2,
        cols: Optional[int] = None,
        rows: Optional[int] = None,
    ) -> ChartConfig:
        """
        Create a radar chart configuration

        Args:
            header: Chart title
            description: Chart description
            series: List of Series objects containing data
            show_grid: Whether to show grid lines
            show_legend: Whether to show the legend
            show_tooltip: Whether to show tooltips on hover
            max_value: Maximum value for radar scale
            fill_opacity: Opacity of area fill
            stroke_width: Width of the outline stroke
            cols: Number of columns (1-4) the chart should span
            rows: Number of rows (1-4) the chart should span

        Returns:
            ChartConfig object for a radar chart
        """
        options = RadarChartOptions(
            showGrid=show_grid,
            showLegend=show_legend,
            showTooltip=show_tooltip,
            maxValue=max_value,
            fillOpacity=fill_opacity,
            strokeWidth=stroke_width,
        )

        size = cls.create_chart_size(cols, rows) if cols or rows else None

        return ChartConfig(
            subtype=ChartSubtype.RADAR,
            header=header,
            description=description,
            series=series,
            options=options,
            size=size,
        )

    @classmethod
    def create_metric_card(
        cls,
        header: str,
        description: str,
        value: Union[float, str],
        value_suffix: Optional[str] = None,
        value_prefix: Optional[str] = None,
        value_formatting: Optional[ValueFormatting] = None,
        icon: Optional[str] = None,
        trend_value: Optional[float] = None,
        trend_direction: Optional[TrendDirection] = None,
        trend_label: Optional[str] = None,
        cols: Optional[int] = None,
        rows: Optional[int] = None,
    ) -> CardConfig:
        """
        Create a metric card configuration

        Args:
            header: Card title
            description: Card description
            value: Main value to display
            value_suffix: Suffix to display after the value
            value_prefix: Prefix to display before the value
            value_formatting: Formatting style for the value
            icon: Icon to display
            trend_value: Value for trend indicator
            trend_direction: Direction of trend ("up" or "down")
            trend_label: Label for trend
            cols: Number of columns (1-4) the card should span
            rows: Number of rows (1-4) the card should span

        Returns:
            CardConfig object for a metric card
        """
        trend = None
        if (
            trend_value is not None
            and trend_direction is not None
            and trend_label is not None
        ):
            trend = Trend(
                value=trend_value, direction=trend_direction, label=trend_label
            )

        size = cls.create_chart_size(cols, rows) if cols or rows else None

        return CardConfig(
            header=header,
            description=description,
            value=value,
            valueSuffix=value_suffix,
            valuePrefix=value_prefix,
            valueFormatting=value_formatting,
            icon=icon,
            trend=trend,
            size=size,
        )

    @staticmethod
    def to_dict(config: Union[ChartConfig, CardConfig]) -> Dict:
        """Convert config model to a dictionary for serialization"""
        return config.dict(by_alias=True, exclude_none=True)

    @staticmethod
    def to_json(config: Union[ChartConfig, CardConfig]) -> str:
        """Convert config model to a JSON string for serialization"""
        return config.json(by_alias=True, exclude_none=True)
