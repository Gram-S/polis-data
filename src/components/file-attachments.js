import {FileAttachment} from "observablehq:stdlib";

export const workbook = await FileAttachment("../polis data_distributed 21.08.25.xlsx").xlsx();
export const polis = workbook.sheet("Sheet1", {headers: true});

// import {workbook, polis} from "./components/file-attachments.js";

