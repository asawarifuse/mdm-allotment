from app.database import SessionLocal
from app.models.admin import Admin
from app.utils.security import hash_password


ADMINS = [
    ("cse_admin",   "Dr. Manoj Bramhe",          "CSE",  "mb_cse"),
    ("csbs_admin",  "Dr. Praveen Sen",           "CSBS", "ps_csbs"),
    ("civil_admin", "Dr. Abhay Hirekhan",        "CV",   "ah_cv"),
    ("ee_admin",    "Dr. Mrs. Jyoti Rothe",      "EE",   "jr_ee"),
    ("etc_admin",   "Dr. Harish Rajurkar",       "ET",   "hr_et"),
    ("it_admin",    "Dr. Mrs. Shabana Pathan",   "IT",   "sp_it"),
    ("me_admin",    "Dr. Sushant Satputaley",    "ME",   "ss_me"),
    ("ai_admin",    "Dr. Vikas Bhowate",         "AI",   "vb_ai"),
    ("ds_admin",    "Dr. Manish Gudadhe",        "DS",   "mg_ds"),
    ("iot_admin",   "Dr. Shriraghavan Madbushi", "IIOT", "sm_iiot"),
    ("cs_admin",    "Dr. Abhishek Pathak",       "CS",   "ap_cs"),
    ("rai_admin",   "Dr. Amit Bhende",           "RAI",  "ab_rai"),
]


def seed():
    db = SessionLocal()
    try:
        inserted = 0
        for admin_id, name, branch, pwd in ADMINS:
            exists = db.query(Admin).filter(Admin.admin_id == admin_id).first()
            if exists:
                continue
            db.add(Admin(
                admin_id=admin_id,
                name=name,
                password_hash=hash_password(pwd),
                role="branch_admin",
                branch=branch,
            ))
            inserted += 1
        db.commit()
        print(f"Inserted {inserted} branch admins.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()