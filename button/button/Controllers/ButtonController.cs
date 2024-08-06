using button.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore.Metadata.Internal;


namespace button.Controllers
{
    public class ButtonController : Controller
    {
        private readonly ButtonclickContext _context;
        

        public ButtonController(ButtonclickContext context)
        {
            _context = context;
        }

        public IActionResult Index()
        {
            
             var model = _context.TopMenu.FirstOrDefault();
            return View(model);
            
        }
    

        public IActionResult Increase()
        {
            var model = _context.TopMenu.FirstOrDefault();
            if (model != null)
            {
                model.Sum++;
                model.ButtonType = "+";
                model.ClickTime = DateTime.Now;
                _context.SaveChanges();
            
            }
            return RedirectToAction("Index");
        }

        public IActionResult Decrease()
        {
            var model = _context.TopMenu.FirstOrDefault();
            if (model != null)
            {
                model.Sum--;
                model.ButtonType = "-";
                model.ClickTime = DateTime.Now;
                _context.SaveChanges();
            }
            return RedirectToAction("Index");
        }
    }
}