package xx;

import org.springframework.beans.BeansException;
import org.springframework.context.ApplicationContext;
import org.springframework.context.ApplicationContextAware;
import org.springframework.stereotype.Component;

@Component
public class SpringApplicationContextHolder implements ApplicationContextAware {

    private static ApplicationContext APP_CONTEXT;

    public static ApplicationContext getApplicationContext() {
        return APP_CONTEXT;
    }


    public void setApplicationContext(ApplicationContext appContext) throws BeansException {
        APP_CONTEXT = appContext;
    }

    /**
     * 获取容器中的Bean对象
     *
     * @param beanName
     * @return
     */
    @SuppressWarnings("unchecked")
    public static <T> T getBeanByName(String beanName) {
        return (T) APP_CONTEXT.getBean(beanName);
    }

    /**
     * 根据类型获取bean
     *
     * @param requiredType
     * @param <T>
     * @return
     */
    public static <T> T getBeanByClass(Class<T> requiredType) {
        return APP_CONTEXT.getBean(requiredType);
    }


}


