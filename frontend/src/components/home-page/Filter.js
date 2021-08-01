import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import InputLabel from "@material-ui/core/InputLabel";
import TextField from "@material-ui/core/TextField";
import FormControl from "@material-ui/core/FormControl";
import Grid from "@material-ui/core/Grid";
import Select from "@material-ui/core/Select";
import Button from "@material-ui/core/Button";

const useStyles = makeStyles((theme) => ({
  root: {
    display: "flex",
    justifyContent: "center",
    marginBottom: theme.spacing(2),
  },
  margin: {
    margin: theme.spacing(1),
  },
  formControl: {
    margin: theme.spacing(1),
    minWidth: 120,
  },
  flex: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  height: {
    maxHeight: "50px",
  },
}));

export default function FilterSelects(props) {
  const classes = useStyles();

  const [filter, setFilter] = React.useState(() => {
    return { init_bid: "", created_date: "-created_date", search: "" };
  });

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFilter((prevValues) => {
      return { ...prevValues, [name]: value };
    });
  };

  const handleSearch = (event) => {
    props.setFilter({ ...filter });
  };

  return (
    <div className={classes.root}>
      <Grid item md={4}>
        <TextField
          variant="outlined"
          margin="normal"
          fullWidth
          id="search"
          label="Search"
          name="search"
          type="search"
          autoComplete="search"
          autoFocus
          onChange={handleChange}
          value={filter.search}
        />
        <div className={classes.flex}>
          <FormControl variant="outlined" className={classes.formControl}>
            <InputLabel htmlFor="date-ordering">Date</InputLabel>
            <Select
              native
              value={filter.created_date}
              onChange={handleChange}
              label="Date"
              inputProps={{ name: "created_date", id: "date-ordering" }}
            >
              <option value={"created_date"}>Oldest</option>
              <option value={"-created_date"}>Newest</option>
            </Select>
          </FormControl>
          <FormControl variant="outlined" className={classes.formControl}>
            <InputLabel htmlFor="price-ordering">Price</InputLabel>
            <Select
              native
              value={filter.init_bid}
              onChange={handleChange}
              label="Price"
              inputProps={{ name: "init_bid", id: "price-ordering" }}
            >
              <option aria-label="None" value="" />
              <option value={"init_bid"}>Ascending</option>
              <option value={"-init_bid"}>Descending</option>
            </Select>
          </FormControl>
          <Button
            onClick={handleSearch}
            classes={{ root: classes.height }}
            variant="contained"
            color="primary"
            disableElevation
          >
            Apply
          </Button>
        </div>
      </Grid>
    </div>
  );
}
