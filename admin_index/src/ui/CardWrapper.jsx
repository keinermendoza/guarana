export function CardWrapper({children, extraClass=null}) {
  return (
    <div className={`p-4 mb-4 border border-solid border-gray-400 rounded-md ${extraClass ? extraClass : ''}`}>{children}</div>
  )
}
