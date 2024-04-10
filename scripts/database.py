from datetime import datetime
import sqlite3


class Database:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def get_subscriptions(self, status=True, use_timer=False):
        with self.connection:
            if use_timer:
                return self.cursor.execute(
                    "SELECT * FROM `subscriptions` WHERE `status` = ? AND `last_send_message` > ?",
                    (status, datetime.now()),
                ).fetchall()
            else:
                return self.cursor.execute(
                    "SELECT * FROM `subscriptions` WHERE `status` = ?", (status,)
                ).fetchall()

    def get_status(self, user_id):
        with self.connection:
            subscription = self.cursor.execute(
                "SELECT last_send_message FROM subscriptions WHERE user_id = ?",
                (user_id,),
            ).fetchone()

            if subscription is not None:
                end_time_str = subscription[0]
                if end_time_str is None:
                    return False

                end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S.%f")

                if end_time > datetime.now():
                    return True
            return False

    def subscriber_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT * FROM `subscriptions` WHERE `user_id` = ?", (user_id,)
            ).fetchall()
            return bool(len(result))

    def add_subscriber(
        self, user_id, status=True, username=None, last_send_message=None
    ):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO `subscriptions` (`user_id`, `status`, `username`, `last_send_message`) VALUES(?,?,?,?)",
                (user_id, status, username, last_send_message),
            )

    def update_subscription(self, user_id, status):
        with self.connection:
            return self.cursor.execute(
                "UPDATE `subscriptions` SET `status` = ? WHERE `user_id` = ?",
                (status, user_id),
            )

    def remove_time(self, user_id):
        with self.connection:
            self.cursor.execute(
                "UPDATE `subscriptions` SET `last_send_message` = ? WHERE `user_id` = ?",
                (datetime.now(), user_id),
            )

    def add_time(self, user_id, time_delta):
        with self.connection:
            result = self.cursor.execute(
                "SELECT * FROM `subscriptions` WHERE `user_id` = ?", (user_id,)
            ).fetchall()
            last_message_user = result[0][4]
            if last_message_user is not None:
                previous_time = datetime.strptime(
                    last_message_user, "%Y-%m-%d %H:%M:%S.%f"
                )
                if previous_time < datetime.now():
                    new_time = datetime.now() + time_delta
                    self.cursor.execute(
                        "UPDATE `subscriptions` SET `last_send_message` = ? WHERE `user_id` = ?",
                        (new_time, user_id),
                    )
                else:
                    new_time = previous_time + time_delta
                    self.cursor.execute(
                        "UPDATE `subscriptions` SET `last_send_message` = ? WHERE `user_id` = ?",
                        (new_time, user_id),
                    )
            else:
                new_time = datetime.now() + time_delta
                self.cursor.execute(
                    "UPDATE `subscriptions` SET `last_send_message` = ? WHERE `user_id` = ?",
                    (new_time, user_id),
                )

    def check_username(self, username):
        if username[0] == "@":
            username = username[1:]
        with self.connection:
            info = self.cursor.execute(
                "SELECT * FROM subscriptions WHERE username=?", (username,)
            ).fetchone()
            info2 = self.cursor.execute(
                "SELECT * FROM subscriptions WHERE user_id=?", (username,)
            ).fetchone()
            if info is None and info2 is None:
                return False
            elif info is not None:
                return [info[1], info[3], info[4]]
            else:
                return [info2[1], info2[3], info2[4]]

    def close(self):
        self.connection.close()

    def is_admin(self, username):
        info = self.cursor.execute(
            "SELECT is_admin FROM subscriptions WHERE username=?", (username,)
        ).fetchone()
        return info

    def add_admin(self, username):
        self.cursor.execute(
            "UPDATE subscriptions SET is_admin = 1 WHERE username=?", (username,))
        return True
