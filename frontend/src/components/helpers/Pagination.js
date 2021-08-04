import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import Pagination from "@material-ui/lab/Pagination";

const useStyles = makeStyles((theme) => ({
  root: {
    "& > * + *": {
      marginTop: theme.spacing(3),
      marginBottom: theme.spacing(3),
      display: "flex",
      justifyContent: "center",
    },
  },
}));

export default function PaginationControlled(props) {
  const classes = useStyles();
  const [page, setPage] = React.useState(props.page);
  const handleChange = (event, value) => {
    setPage(value);
    props.history.push(`/${value}/`);
  };

  return (
    <div className={classes.root}>
      <Typography classes={{ root: "pagination-page-text" }}>
        Page: {page}
      </Typography>
      <Pagination
        count={props.count}
        page={page}
        boundaryCount={1}
        onChange={handleChange}
      />
    </div>
  );
}
