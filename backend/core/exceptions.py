from datetime import datetime


class AuctionItemExpired(Exception):
    """
    Exception raised when auction close date past current date

    Parameters:
        close_date -- auction close date for the item in server timezone
        current_date -- current date in server timezone
    """

    def __init__(self, close_date: datetime, current_date: datetime) -> None:
        self.message = f"""Auction already ended for the item: 
        current date - {current_date}, auction close date - {close_date}"""
        super().__init__(self.message)
