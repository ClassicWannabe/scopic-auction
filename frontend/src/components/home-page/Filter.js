import React from "react";
import { makeStyles, withStyles } from "@material-ui/core/styles";
import InputLabel from "@material-ui/core/InputLabel";
import MenuItem from "@material-ui/core/MenuItem";
import FormControl from "@material-ui/core/FormControl";
import Select from "@material-ui/core/Select";
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

export default function FilterSelects() {
  const classes = useStyles();
  const [dropdown, setDropdown] = React.useState(() => {
    return { price: "", date: "new" };
  });
  const handleChange = (event) => {
    const { name, value } = event.target;
    setDropdown((prevValues) => {
      return { ...prevValues, [name]: value };
    });
  };
  return (
    <div>
      <FormControl className={classes.margin}>
        <InputLabel htmlFor="item-title">Name</InputLabel>
        <BootstrapInput id="item-title" />
      </FormControl>
      <FormControl className={classes.margin}>
        <InputLabel htmlFor="item-description">Description</InputLabel>
        <BootstrapInput id="item-description" />
      </FormControl>
      <FormControl className={classes.margin}>
        <InputLabel htmlFor="date-ordering">Date</InputLabel>
        <NativeSelect
          id="date-ordering"
          value={dropdown.date}
          name="date"
          onChange={handleChange}
          input={<BootstrapInput />}
        >
          <option value={"new"}>Newest</option>
          <option value={"old"}>Oldest</option>
        </NativeSelect>
      </FormControl>
      <FormControl className={classes.margin}>
        <InputLabel htmlFor="price-ordering">Price</InputLabel>
        <NativeSelect
          id="price-ordering"
          value={dropdown.price}
          name="price"
          onChange={handleChange}
          input={<BootstrapInput />}
        >
          <option aria-label="None" value="" />
          <option value={"ASC"}>ASC</option>
          <option value={"DESC"}>DESC</option>
        </NativeSelect>
      </FormControl>
    </div>
  );
}
