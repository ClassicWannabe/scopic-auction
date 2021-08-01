import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Card from "@material-ui/core/Card";
import CardActionArea from "@material-ui/core/CardActionArea";
import CardActions from "@material-ui/core/CardActions";
import CardContent from "@material-ui/core/CardContent";
import CardMedia from "@material-ui/core/CardMedia";
import Button from "@material-ui/core/Button";
import Typography from "@material-ui/core/Typography";
import Grid from "@material-ui/core/Grid";

const useStyles = makeStyles({
  root: {
    maxWidth: 345,
  },
});

export default function AuctionItem(props) {
  const classes = useStyles();

  const redirect = () => {
    props.history.push(`/item/${props.id}`);
  };

  const truncateText = (str) => {
    return str.length > 50 ? str.substring(0, 50) + "..." : str;
  };

  return (
    <Grid item md={3}>
      <Card className={classes.root}>
        <CardActionArea onClick={redirect}>
          <CardMedia
            component="img"
            alt={props.title}
            height="140"
            image={props.compressedPicture}
            title={props.title}
          />
          <CardContent>
            <Typography gutterBottom variant="h5" component="h2">
              {props.title}
            </Typography>
            <Typography variant="body2" color="textSecondary" component="p">
              {truncateText(props.description)}
            </Typography>
          </CardContent>
        </CardActionArea>
        <CardActions classes={{ root: "card-footer-group" }}>
          <Typography variant="body2" color="textSecondary" component="p">
            Starting price: ${props.initBid}
          </Typography>
          <Button onClick={redirect} size="small" color="primary">
            Bid
          </Button>
        </CardActions>
      </Card>
    </Grid>
  );
}
