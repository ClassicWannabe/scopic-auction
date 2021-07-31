import React from "react";
import { makeStyles, withStyles } from "@material-ui/core/styles";
import InputLabel from "@material-ui/core/InputLabel";
import TextField from "@material-ui/core/TextField";
import FormControl from "@material-ui/core/FormControl";
import NativeSelect from "@material-ui/core/NativeSelect";
import InputBase from "@material-ui/core/InputBase";

const BootstrapInput = withStyles((theme) => ({
  root: {
    "label + &": {
      marginTop: theme.spacing(3),
    },
  },
  input: {
    borderRadius: 4,
    position: "relative",
    backgroundColor: theme.palette.background.paper,
    border: "1px solid #ced4da",
    fontSize: 16,
    padding: "10px 26px 10px 12px",
    transition: theme.transitions.create(["border-color", "box-shadow"]),
    fontFamily: [
      "-apple-system",
      "BlinkMacSystemFont",
      '"Segoe UI"',
      "Roboto",
      '"Helvetica Neue"',
      "Arial",
      "sans-serif",
      '"Apple Color Emoji"',
      '"Segoe UI Emoji"',
      '"Segoe UI Symbol"',
    ].join(","),
    "&:focus": {
      borderRadius: 4,
      borderColor: "#80bdff",
      boxShadow: "0 0 0 0.2rem rgba(0,123,255,.25)",
    },
  },
}))(InputBase);

const useStyles = makeStyles((theme) => ({
  margin: {
    margin: theme.spacing(1),
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

  return (
    <div>
      <TextField
        variant="outlined"
        margin="normal"
        fullWidth
        id="search"
        label="Search"
        name="search"
        autoComplete="search"
        autoFocus
        onChange={handleChange}
        value={filter.search}
      />
      <FormControl className={classes.margin}>
        <InputLabel htmlFor="date-ordering">Date</InputLabel>
        <NativeSelect
          id="date-ordering"
          value={props.filter.date}
          name="created_date"
          onChange={handleChange}
          input={<BootstrapInput />}
        >
          <option value={"created_date"}>Oldest</option>
          <option value={"-created_date"}>Newest</option>
        </NativeSelect>
      </FormControl>
      <FormControl className={classes.margin}>
        <InputLabel htmlFor="price-ordering">Price</InputLabel>
        <NativeSelect
          id="price-ordering"
          value={filter.init_bid}
          name="init_bid"
          onChange={handleChange}
          input={<BootstrapInput />}
        >
          <option aria-label="None" value="" />
          <option value={"init_bid"}>ASC</option>
          <option value={"-init_bid"}>DESC</option>
        </NativeSelect>
      </FormControl>
    </div>
  );
}
