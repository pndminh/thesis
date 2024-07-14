import asyncio
from frontend.pages.utils import fetch, handle_extract


async def run():
    url = "https://baotintuc.vn/y-te/nhung-cuoc-doi-lam-lo-quay-dau-lam-lai-nho-thuoc-methadone-20240714174508327.htm"
    dynamic_fetch_options = {
        "infinite_scroll": 0,
        "expand_button_click": "",
        "pagination": 0,
    }
    html_list = await fetch(
        url, "Dynamic fetch", dynamic_fetch_options=dynamic_fetch_options
    )
    contents_to_extract = {
        "title": [("Những cuộc đời lầm lỡ 'quay đầu' làm lại nhờ thuốc Methadone", [])],
        "description": [("Nhiều người tham gia điều trị nghiện", [])],
        "content": [("Nhìn người thanh niên 30 tuổi gầy rạc, khuôn mặt hốc hác", [])],
    }
    contents = await handle_extract(
        html_list, contents_to_extract, batch=False, extract_type="Direct Path Extract"
    )
    print(contents)


if __name__ == "__main__":
    asyncio.run(run())
