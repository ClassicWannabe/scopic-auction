import React, { useState, useEffect } from "react";
import Container from "@material-ui/core/Container";
import AuctionItem from "./AuctionItem";
import Filter from "./Filter";
import Pagination from "../helpers/Pagination";
import { getItems } from "../../authorization/apiCalls";

export default function Home(props) {
  const page = props.match.params.page;

  const [items, setItems] = useState([]);
  const [filter, setFilter] = React.useState(() => {
    return { init_bid: "", created_date: "-created_date", search: "" };
  });
  const [paginator, setPaginator] = useState(1);

  useEffect(() => {
    const clean_filter = Object.fromEntries(
      Object.entries(filter).filter(([_, v]) => v !== null && v !== "")
    );

    getItems(clean_filter, page)
      .then((response) => {
        if (
          response !== undefined &&
          response.status === 200 &&
          response.data.results?.length > 0
        ) {
          setItems(response.data.results);
          setPaginator(
            Math.ceil(response.data.count / response.data.page_size)
          );
        }
      })
      .catch((error) => console.error(error));
  }, [page]);

  return (
    <div>
      <Container component="main" maxWidth="xs">
        <Filter setFilter={setFilter} filter={filter} />
        {items.length > 0 &&
          items.map((item) => {
            return (
              <AuctionItem
                key={item.id}
                title={item.title}
                description={item.description}
                compressed_picture={item.compressed_picture}
              />
            );
          })}
        <Pagination {...props} count={paginator} />
      </Container>
    </div>
  );
}
