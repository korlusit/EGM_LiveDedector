import sys
from PyQt6.QtWidgets import QApplication
from arayuz import EGMSistem
def test_dashboard_initialization():
    app = QApplication(sys.argv)
    print("Testing with user: onur_komiser")
    window = EGMSistem(user_name="onur_komiser")
    expected_name = "Onur KOMISER"
    actual_name = window.personel_verisi["ad"]
    print(f"Profile Name: Expected='{expected_name}', Actual='{actual_name}'")
    assert actual_name == expected_name, f"Profile Name Mismatch! Got {actual_name}"
    expected_pts = "PLAKA TANIMA SİSTEMİ (PTS)"
    actual_pts = window.ui.label_4.text()
    print(f"PTS Label: Expected='{expected_pts}', Actual='{actual_pts}'")
    assert expected_pts in actual_pts, f"PTS Label Mismatch! Got {actual_pts}"
    expected_gbt = "YÜZ TANIMA SİSTEMİ (GBT)"
    actual_gbt = window.ui.label_5.text()
    print(f"GBT Label: Expected='{expected_gbt}', Actual='{actual_gbt}'")
    assert expected_gbt in actual_gbt, f"GBT Label Mismatch! Got {actual_gbt}"
    print("ALL TESTS PASSED!")
if __name__ == "__main__":
    try:
        test_dashboard_initialization()
    except Exception as e:
        print(f"TEST FAILED: {e}")
        sys.exit(1)
