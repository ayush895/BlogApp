try:
    import pymysql
    pymysql.install_as_MySQLdb()
except Exception:
    # If PyMySQL isn't installed yet, Django startup will still fail until it's installed.
    pass

