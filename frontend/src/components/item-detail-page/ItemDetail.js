import React, { useEffect, useState } from "react";
import moment from "moment";
import Container from "@material-ui/core/Container";
import { makeStyles } from "@material-ui/core/styles";
import Card from "@material-ui/core/Card";
import CardActions from "@material-ui/core/CardActions";
import CardContent from "@material-ui/core/CardContent";
import Button from "@material-ui/core/Button";
import Typography from "@material-ui/core/Typography";
import Grid from "@material-ui/core/Grid";
import Modal from "@material-ui/core/Modal";
import TextField from "@material-ui/core/TextField";
import InputAdornment from "@material-ui/core/InputAdornment";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import Checkbox from "@material-ui/core/Checkbox";
import {
  getSpecificItem,
  getBid,
  getOwnBid,
  makeBid,
  updateUserDetails,
} from "../../api/apiCalls";
import "./ItemDetail.css";

function rand() {
  return Math.round(Math.random() * 20) - 10;
}

function getModalStyle() {
  const top = 50 + rand();
  const left = 50 + rand();

  return {
    top: `${top}%`,
    left: `${left}%`,
    transform: `translate(-${top}%, -${left}%)`,
  };
}

const useStyles = makeStyles((theme) => ({
  root: {
    minWidth: 275,
  },
  title: {
    fontSize: 14,
  },
  left: { textAlign: "left" },
  pos: {
    marginBottom: 12,
  },
  paper: {
    position: "absolute",
    maxWidth: 400,
    minWidth: 300,
    backgroundColor: theme.palette.background.paper,
    border: "2px solid #000",
    boxShadow: theme.shadows[5],
    padding: theme.spacing(2, 4, 3),
  },
}));

export default function ItemDetail(props) {
  const id = props.match.params.itemId;
  const userId = localStorage ? localStorage.getItem("user_id") : null;
  const classes = useStyles();
  const currentDateTime = new Date();

  const [item, setItem] = useState({
    init_bid: 0,
    compressed_picture: "",
    title: "",
    description: "",
  });
  const [highestBid, setHighestBid] = useState({ id: 0, bid_amount: 0 });
  const [userBid, setUserBid] = useState({
    id: 0,
    bid_amount: 0,
    auto_bidding: false,
  });
  const [modalStyle] = useState(getModalStyle);
  const [openModal, setOpenModal] = useState(false);
  const [closeDate, setCloseDate] = useState(new moment.duration(0));
  const [bidClosed, setBidClosed] = useState(false);
  const [newBid, setNewBid] = useState(0);
  const [maxBid, setMaxBid] = useState(
    localStorage ? localStorage.getItem("max_auto_bid") : 0
  );
  const [autoBidding, setAutoBidding] = useState(false);
  const [trigger, setTrigger] = useState(false);
  const [errors, setErrors] = useState(() => {
    return {
      newBid: { isActive: false, text: "" },
      maxBid: {
        isActive: false,
        text: "This value will be split between all items",
      },
    };
  });

  const formatDecimal = (decimal) => {
    return parseFloat(decimal).toFixed(2);
  };

  const handleModalOpen = () => {
    setOpenModal(true);
  };

  const handleModalClose = () => {
    setOpenModal(false);
  };

  const handleBidChange = (event) => {
    const value = event.target.value;
    setNewBid(value);
  };

  const handleAutoBidding = (event) => {
    const checked = event.target.checked;

    setAutoBidding(checked);
  };

  const handleMaxBidChange = (event) => {
    const value = event.target.value;
    setMaxBid(value);
  };

  const handleBidSubmit = (event) => {
    event.preventDefault();
    if (userBid.id) {
      const data = {
        bid_amount: formatDecimal(newBid),
        auto_bidding: autoBidding,
      };
      makeBid(data, { id: userBid.id })
        .then((response) => {
          if (response && response.status === 200) {
            handleError("newBid", false, "");
          }
        })
        .catch((error) => {
          if (error.response?.data?.message) {
            handleError("newBid", true, error.response.data.message);
          }
        })
        .finally(() => setTrigger(!trigger));
    } else {
      const data = {
        auction_item: id,
        bid_amount: formatDecimal(newBid),
        auto_bidding: autoBidding,
      };
      makeBid(data, { create: true })
        .then((response) => {
          if (response && response.status === 201) {
            handleError("newBid", false, "");
          }
        })
        .catch((error) => {
          if (error.response?.data?.message) {
            handleError("newBid", true, error.response.data.message);
          }
        })
        .finally(() => setTrigger(!trigger));
    }
  };

  const handleError = (target, isActive, text) => {
    setErrors((prevValues) => {
      return {
        ...prevValues,
        [target]: { isActive: isActive, text: text },
      };
    });
  };

  const handleAutoBidSubmit = (event) => {
    event.preventDefault();

    updateUserDetails({ max_auto_bid_amount: formatDecimal(maxBid) })
      .then((response) => {
        if (response && response.status === 200) {
          localStorage.setItem(
            "max_auto_bid",
            response.data?.max_auto_bid_amount
          );
          if (userBid.id) {
            makeBid({ auto_bidding: autoBidding }, { id: userBid.id })
              .then((response) => {
                if (response && response.status === 200) {
                  handleError(
                    "maxBid",
                    false,
                    "This value will be split between all items"
                  );
                  handleModalClose();
                }
              })
              .catch((error) => {
                if (error.response?.data?.message) {
                  handleError("maxBid", true, error.response.data.message);
                }
              });
          }
        }
      })
      .catch((error) => console.error(error))
      .finally(() => setTrigger(!trigger));
  };

  useEffect(() => {
    getSpecificItem(id)
      .then((response) => {
        if (response && response.data && response.status === 200) {
          setItem(response.data);

          if (response.data.bids.length > 0) {
            getBid(response.data.bids[0]).then((response) => {
              if (response && response.data && response.status === 200) {
                setHighestBid(response.data);
                setNewBid(parseFloat(response.data.bid_amount) + 1);
              }
            });
          }

          if (response.data.bidders.includes(parseInt(userId))) {
            getOwnBid(id).then((response) => {
              if (response && response.data && response.status === 200) {
                setUserBid(response.data);
                setAutoBidding(response.data.auto_bidding);
              }
            });
          }
        }
      })
      .catch((error) => console.error(error));
  }, [id, trigger]);

  useEffect(() => {
    if (item?.bid_close_date && closeDate.asSeconds() >= 0) {
      setTimeout(() => {
        setCloseDate(
          new moment.duration(new Date(item.bid_close_date) - currentDateTime)
        );
      }, 1000);
    } else if (closeDate.asSeconds() < 0) {
      setBidClosed(true);
    }
  }, [currentDateTime]);

  const durations = {
    days: Math.floor(closeDate.asDays()),
  };
  durations.hours = Math.floor(closeDate.asHours()) - durations.days * 24;
  durations.minutes =
    Math.floor(closeDate.asMinutes()) -
    durations.days * 24 * 60 -
    durations.hours * 60;
  durations.seconds =
    Math.floor(closeDate.asSeconds()) -
    durations.days * 24 * 3600 -
    durations.hours * 3600 -
    durations.minutes * 60;

  return (
    <Container className="item-detail" component="main">
      <Modal
        open={openModal}
        onClose={handleModalClose}
        aria-labelledby="simple-modal-title"
        aria-describedby="simple-modal-description"
      >
        <div style={modalStyle} className={classes.paper}>
          <form onSubmit={handleAutoBidSubmit}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={autoBidding}
                  onChange={handleAutoBidding}
                  name="autoBidding"
                />
              }
              label="Auto-bidding function"
            />
            <div className="push10" />
            {autoBidding && (
              <TextField
                id="max-bid-amount"
                label="Max bid amount"
                type="number"
                error={errors.maxBid.isActive}
                helperText={errors.maxBid.text}
                classes={{ root: "bid-input" }}
                value={maxBid}
                onChange={handleMaxBidChange}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">$</InputAdornment>
                  ),
                }}
                InputLabelProps={{
                  shrink: true,
                }}
                variant="outlined"
              />
            )}

            <div className="push20" />

            <Button
              type="submit"
              size="medium"
              variant="contained"
              color="secondary"
              classes={{ root: "bid-submit" }}
            >
              Submit
            </Button>
          </form>
        </div>
      </Modal>
      <Grid container spacing={2}>
        <Grid item md={8}>
          <img
            className="item-picture"
            src={item.compressed_picture}
            alt={item.title}
          />
          <Typography variant="h3">{item.title}</Typography>
          <Typography variant="h5" align="left">
            Description:
          </Typography>
          <Typography align="justify">{item.description}</Typography>
        </Grid>
        <Grid item md={4} sm={12}>
          <Grid container justifyContent="center">
            <Card className={(classes.root, "bid-card")} variant="outlined">
              <form onSubmit={handleBidSubmit}>
                <CardContent>
                  <Typography
                    className={classes.title}
                    color="textSecondary"
                    gutterBottom
                  >
                    {bidClosed ? (
                      "The auction ended"
                    ) : (
                      <span>
                        Ends in {durations.days} days, {durations.hours} hours,{" "}
                        {durations.minutes} minutes, {durations.seconds} seconds
                      </span>
                    )}
                  </Typography>
                  <Typography variant="h5" component="h2">
                    Highest bid: ${highestBid.bid_amount}{" "}
                    {highestBid.id > 0 && highestBid.id === userBid.id && (
                      <b>- your bid</b>
                    )}
                  </Typography>
                  <Typography className={classes.pos} color="textSecondary">
                    Starting bid: ${item.init_bid}
                  </Typography>
                  <Typography variant="body2" component="p">
                    Your last bid: ${userBid.bid_amount}
                  </Typography>
                  {!bidClosed && (
                    <TextField
                      id="bid-amount"
                      error={errors.newBid.isActive}
                      helperText={errors.newBid.text}
                      label="Bid"
                      type="number"
                      classes={{ root: "bid-input" }}
                      value={newBid}
                      onChange={handleBidChange}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">$</InputAdornment>
                        ),
                        step: 2,
                      }}
                      InputLabelProps={{
                        shrink: true,
                      }}
                      variant="outlined"
                    />
                  )}
                </CardContent>
                <CardActions>
                  {!bidClosed && (
                    <Button
                      type="submit"
                      size="small"
                      variant="contained"
                      color="secondary"
                    >
                      Bid
                    </Button>
                  )}
                  {userBid.id && !bidClosed ? (
                    <Button onClick={handleModalOpen} size="small">
                      Change bidding settings
                    </Button>
                  ) : null}
                </CardActions>
              </form>
            </Card>
          </Grid>
        </Grid>
      </Grid>
    </Container>
  );
}
