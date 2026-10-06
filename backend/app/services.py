"""缫丝盆门槛。

- 登汤温：已缫完盆封盘，不再收汤温（不重定向到邻盆）。
- 标已缫完：须最近一次汤温落在 38～42℃。
- 拨浸茧 / 改缫丝中：只改盆态，不看汤温、不看邻盆。
"""

from app.models import Basin

MIN_TEMP = 38.0
MAX_TEMP = 42.0


class RuleError(ValueError):
    pass


def latest_temp(basin: Basin) -> float | None:
    if not basin.readings:
        return None
    latest = max(basin.readings, key=lambda r: r.taken_at)
    return latest.water_temp_c


def assert_can_add_reading(basin: Basin) -> None:
    """登汤温只认本盆盆态——已缫完封盘，与汤温高低、邻盆均无关。"""
    if basin.status == Basin.STATUS_REELED:
        raise RuleError(f"{basin.code} 已缫完封盘，不能再登记汤温")


def assert_can_set_status(basin: Basin, new_status: str) -> None:
    """改态门槛：只有「标已缫完」吃 38～42℃ 汤温带；拨浸茧不吃。"""
    allowed = {Basin.STATUS_SOAKING, Basin.STATUS_REELING, Basin.STATUS_REELED}
    if new_status not in allowed:
        raise RuleError(f"无效状态：{new_status}")
    if new_status != Basin.STATUS_REELED:
        return
    temp = latest_temp(basin)
    if temp is None:
        raise RuleError("该盆尚无汤温记录，不能标已缫完")
    if temp < MIN_TEMP or temp > MAX_TEMP:
        raise RuleError(
            f"最近汤温 {temp}℃ 不在 {MIN_TEMP:.0f}～{MAX_TEMP:.0f}℃，不能标已缫完"
        )
