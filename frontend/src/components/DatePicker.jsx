import { FormInput } from "./FormInput";

export function DatePicker(props) {
  return <FormInput type={props.withTime ? "datetime-local" : "date"} {...props} />;
}
